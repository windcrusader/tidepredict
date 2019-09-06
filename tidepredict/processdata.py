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
from datetime import datetime, timedelta
from tidepredict.tide import Tide
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import io
import zipfile
import sys
from ftplib import FTP
import calendar
from pytz import timezone
from jinja2 import Environment, FileSystemLoader
import os
from tidepredict import ftp_helpers
from tidepredict import process_station_list

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
        sys.exit()
    return ftpurl  

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
    sio = ftp_helpers.get_byte_stream("ftp.soest.hawaii.edu",
                                      "uhslc/rqds/pacific/hourly/h551a.zip")
    for year in years:
        #try to open the downloaded zip archive
        try:
            zarchive = zipfile.ZipFile(sio)
        except zipfile.BadZipfile:
            print("Could not open zip archive")
            sys.exit()

        #print(zarchive)
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
            #print(linedc)
            tideheights = linedc.split()[3:15]
            dateraw = linedc.split()[2]
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

def plot_data(datalist):
    """Plots the timestamp tide heights.

    This is useful for validating data
    """     
    print("Plotting tide data")
    df = pd.DataFrame(datalist, columns=['Date', 'DateValue'])
    #dump to file
    mydir = os.path.dirname(os.path.realpath(__file__))
    df.to_csv(os.path.join(mydir,"tidedata.csv"))
    print(df.head())
    df.plot()
    print("Close plot window to continue")
    plt.show()
    
    

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
        t.append(datetime.strptime(dt, "%Y-%m-%d %H:%M:%S"))
        heights.append(float(height))

    ##Fit the tidal data to the harmonic model using Pytides
    print("Fitting harmonic model")
    print(heights[:5])
    print(t[:5])
    my_tide = Tide.decompose(np.array(heights), np.array(t))
    return my_tide

def output_html(my_tide, month, year):
    """ Dumps a html page of a calendar month of tide predictions
        todo: generalise
    """
    ##Prepare our variables for the template
    location = "Lyttelton, NZ"
    tzname = "US/Pacific"
    tz = timezone(tzname)
    utc = timezone('UTC')
    datum = "MLLW"
    units = "metres"
    rows = []
    print("Running tide prediction")
    for day in range(1,calendar.monthrange(year,month)[1] + 1):
        start = tz.localize(datetime(year, month, day))
        end = start + timedelta(days=1)
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
            time = time + timedelta(minutes=time.second > 30)
            height = e[1]
            extrema.append({'time': time.strftime('%H:%M'), 'height': "{0:.2f}".format(height)})
        #This is just for nicer formatting of days with only three tides
        for _ in range(4 - len(extrema)):
            extrema.append({'time': '', 'height': ''})
        rows.append([date, extrema])

    ##Render our template
    #print(" ".join(rows))
    #get the current working directory - this is useful on windows machines
    mydir = os.path.dirname(os.path.realpath(__file__))
    print(mydir)
    env = Environment(loader=FileSystemLoader(mydir),trim_blocks=True)
    template = env.get_template('template.html')
    with open(os.path.join(mydir,"output.html"), "w") as fh:
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

    process_station_list.create_station_dataframe()

    sys.exit()

    datadict = process_unhw_data(ftpurl = get_data_url(ocean = "pacific"))
    plot_data(datadict)
    my_tides = fit_model(datadict)
    print(my_tides)
    output_html(my_tides, 9, 2019)
