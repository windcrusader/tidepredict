"""
Tide Predictor

Generates tide predictions using the pytides module.

Convert University of Hawaii research quality datasets into tidal
harmonic constituents for making predictions on any location that data
exists for.

Datasets and background info available from:
ftp://ftp.soest.hawaii.edu/uhslc/rqds/
"""
from __future__ import print_function
import datetime
from tidepredict.tide import Tide
import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd
import io
import zipfile
import sys
from ftplib import FTP
import calendar
import pytz
from jinja2 import Environment, FileSystemLoader
from tidepredict import ftp_helpers
from tidepredict import constants
import json
from tidepredict import constituent
import dateutil
import pathlib

def get_data_url(ocean = "pacific"):
    """returns the data file url for the uhslc server for a specific
    ocean area.

    accepted inputs are one of the following locations:
    pacific
    indian
    atlantic
    """
    #do string.lower to make it match for any case (user friendly)
    if ocean.lower() == "pacific":
        ftpurl = "uhslc/rqds/pacific"
    elif ocean.lower() == "atlantic":
        ftpurl = "uhslc/rqds/atlantic"
    elif ocean.lower() == "indian":
        ftpurl = "uhslc/rqds/indian"
    else:
        raise Exception("Ocean must be one of: Indian, Pacific, or Atlantic")
        sys.exit(1)
    return ftpurl  

def predict_plain(tide, station_dict, format, timeobj):
    """
    Generates tide predictions similar to Xtide's plain mode.
    startdate for prediction (Python datetime)
    enddate:  enddate for prediction
    tide: the tide model to use
    """
    
    if format == "t":
        extrema = "Tide forecast for %s, %s\n" %(station_dict['name'],
                                        station_dict['country'])
        extrema += "Latitude:%5.2f Longitude:%5.2f\n" %(station_dict['lat'],
                                        station_dict['lon'])                                                                
    else:
        extrema = ""

    extremaUTC = tide.extrema(timeobj.st_utc, timeobj.en_utc)
    #print(extremaUTC)
    
    for e in extremaUTC:
        #print(e)
        #get localised time
        time = timeobj.localise(e[0])
        height = e[1]
        if format == "c":
            #csv so append station name
            extrema += station_dict['name'] + ","
            extrema += time.strftime("%Y-%m-%d,%H%M")
        else:
            extrema += time.strftime("%Y-%m-%d %H%M")
        
        if format == "c":
            extrema += ",%s," %timeobj.tz
        else:
            extrema += " %s" %timeobj.tz

        extrema += "%5.2f" %height   

        if format == "c":
            extrema += ","
        
        if e[2] == "L":
            extrema += " Low Tide"
        else:
            extrema += " High Tide"
        extrema += "\n"    
    
    return extrema


def reconstruct_tide_model(station_dict, loc_code):
    """
    Method to reconstruct the tide model from the dictionary of all stations
    input: tm_file, which is the open json file
    """
    try:
        constits = [constituent.__getattribute__("_"+cstr) 
                for cstr in station_dict[loc_code]['cons']]
    except KeyError:
        return None

    model = np.zeros(len(station_dict[loc_code]['cons']), dtype = Tide.dtype)
    assert len(constits) == len(station_dict[loc_code]['amps']) \
            == len(station_dict[loc_code]['phase']), \
           "model file arrays must be equal length"
    model['constituent'] = constits
    model['amplitude'] = station_dict[loc_code]['amps']
    model['phase'] = station_dict[loc_code]['phase']
    tide = Tide(model = model, radians = False)
    return tide

def process_unhw_data(ftpurl, years = [15,16], loc_code = "h551a"):
    """Processes university of Hawaii data into a Python dictionary.

    Inputs:
    years: years of data (default most recent two years) as a list of 
           year ints
    location: unhw code for the location to retrieve. Default: Lyttelton, NZ

    Outputs:
    Dictionary in the form of {DateTime:TideLevel}
    timestamps are hourly.

    """
    datalist = []  
    #print(zipdat)
    #print(filedata)
    sio = ftp_helpers.get_byte_stream(constants.FTP_BASE,
                                      "%s/hourly/%s.zip"%(ftpurl,loc_code))
    for year in years:
        #try to open the downloaded zip archive
        try:
            zarchive = zipfile.ZipFile(sio)
        except zipfile.BadZipfile:
            print("Could not open zip archive")
            sys.exit()

        #print(zarchive)
        if year > int(str(datetime.datetime.today().year)[:-2]):
            #assume pre 2000 so h prefix required.
            datfile = "h%s%i.dat"%(loc_code[1:],year)
        else:    
            datfile = "i%s%i.dat"%(loc_code[1:],year)
        print("Opening data file:%s"%datfile)
        try:
            fdat = zarchive.open(datfile, "r")
        except RuntimeError:
            print('RuntimeError')
            sys.exit()

        #so we have the file data now read it line by line
        for i, line in enumerate(fdat):
            #ignore header info on the first row
            #todo should try and check file validity here.
            if i == 0:
              continue
            #print(line.decode("UTF-8"))
            linedc = line.decode("UTF-8")
            #tide height data starts at column 22 (py index = 21)
            tideheights = linedc[21:].split()
            #date data starts at column 12(11) ends at 20 
            dateraw = linedc[11:20]
            dateactual = ( dateraw[:4] + "-" + dateraw[4:6] + "-" + dateraw[6:8]
                        )
                
            for j,item in enumerate(tideheights):
                #check for bad data 
                if int(item) == 9999 or int(item) == -9999:
                    continue
                datakey = dateactual
                if dateraw[8] == "1":
                    datakey += " %02d" %(j) + ":00:00"
                else:
                    datakey += " %02d" %(j + 12) + ":00:00"
                data = float(item)/1000
                datalist.append([datakey, data])
        fdat.close()
    return datalist

def output_to_file(datalist):
    """Outputs the processed datadict to a textfile
    
        Mainly used for debugging purposes
    """
    f2 = open("unhw_processed.dat", "w")
    for item in datalist:
       print("%s %s" %(item[0], item[1]), file = f2)
    f2.close()

def fit_model(datalist):
    """Fits harmonic model to tides using pytides
    """

    t = []
    heights = []
    for dt, height in datalist:
        #print(line.split()[:2])
        t.append(datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S"))
        heights.append(float(height))

    ##Fit the tidal data to the harmonic model using Pytides
    print("Fitting harmonic model")
    #print(heights[:5])
    #print(t[:5])
    my_tide = Tide.decompose(np.array(heights), np.array(t))
    return my_tide

def output_html(my_tide, month, year):
    """ Dumps a html page of a calendar month of tide predictions
        todo: generalise
    """
    ##Prepare our variables for the template
    location = "Lyttelton, NZ"
    tzname = "Pacific/Auckland"
    tz = datetime.timezone(tzname)
    utc = datetime.timezone('UTC')
    datum = "MLLW"
    units = "metres"
    rows = []
    print("Running tide prediction")
    for day in range(1,calendar.monthrange(year,month)[1] + 1):
        start = tz.localize(datetime.datetime(year, month, day))
        end = start + datetime.timedelta(days=1)
        startUTC = utc.normalize(start.astimezone(utc))
        endUTC = utc.normalize(end.astimezone(utc))
        extremaUTC = my_tide.extrema(startUTC, endUTC)
        date = {'date': day, 'day': calendar.day_abbr[start.weekday()]}
        extrema = []
        for e in extremaUTC:
            e = list(e)
            #print(e)
            time = tz.normalize(e[0].astimezone(tz))
            ##Round the time to the nearest minute
            time = time + datetime.timedelta(minutes=time.second > 30)
            height = e[1]
            extrema.append({'time': time.strftime('%H:%M'), 'height': "{0:.2f}".format(height)})
        #This is just for nicer formatting of days with only three tides
        for _ in range(4 - len(extrema)):
            extrema.append({'time': '', 'height': ''})
        rows.append([date, extrema])

    ##Render our template
    #print(" ".join(rows))
    #get the current working directory - this is useful on windows machines
    mydir = pathlib.Path.home()
    print(mydir)
    env = Environment(loader=FileSystemLoader(mydir),trim_blocks=True)
    template = env.get_template('template.html')
    with open(mydir / "output.html", "w") as fh:
        print(template.render(
        location = location,
        tzname = tzname,
        datum = datum,
        units = units,
        year = year,
        month = calendar.month_name[month],
        data = rows
        ), file = fh)    

if __name__ == "__main__":
    pass
    #plot_data(datadict)
    #output_html(my_tides, 9, 2019)
