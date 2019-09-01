"""
Tide Predictor

Generates tide predictions using the pytides module.

Convert University of Hawaii research quality datasets into tidal
harmonic constituents for making predictions on any location that data
exists for.

Datasets and background info available from:
ftp://ftp.soest.hawaii.edu/uhslc/rqds/
"""

from datetime import datetime, timedelta
from tide import Tide
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import requests
import io
import zipfile
import sys
from ftplib import FTP
from io import BytesIO
import calendar
from pytz import timezone
from jinja2 import Environment, FileSystemLoader


def process_unhw_data(years = [16,17], loc_code = "h667a"):
    """Processes university of Hawaii data into a Python dictionary.

    Inputs:
    years: years of data (default most recent two years) as a list of 
           year ints
    location: unhw code for the location to retrieve. Default: Lyttelton, NZ

    Outputs:
    Dictionary in the form of {DateTime:TideLevel}
    timestamps are hourly.

    """
    datadict = {}  
    #print(f'ftp://ftp.soest.hawaii.edu/uhslc/rqds/pacific/hourly/{loc_code}.zip')
    ftp = FTP('ftp.soest.hawaii.edu')
    ftp.login() # Username: anonymous password: anonymous@
    sio = BytesIO()
    def handle_binary(more_data):
        sio.write(more_data)

    ftpstring = f"RETR uhslc/rqds/pacific/hourly/{loc_code}.zip"
    print(f"ftp request:{ftpstring}")
    resp = ftp.retrbinary(ftpstring, callback=handle_binary)
    sio.seek(0) # Go back to the start

    #print(zipdat)
    #print(filedata)
    for year in years:
        #try to open the downloaded zip archive
        try:
            zarchive = zipfile.ZipFile(sio)
        except zipfile.BadZipfile:
            print("Could not open zip archive")
            sys.exit()

        #print(zarchive)
        datfile = f'i{loc_code[1:]}{year}.dat'
        print(f"Opening data file:{datfile}")
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
                datadict[datakey] = data
        fdat.close()
    return datadict

def plot_data(datadict):
    """Plots the timestamp tide heights.

    This is useful for validating data
    """     
    print("Plotting tide data")
    df = pd.DataFrame(list(datadict.items()), columns=['Date', 'DateValue'])
    #print(df.head())
    df.plot()
    plt.show()
    print("Close plot window to continue")
    

def output_to_file(datadict):
    """Outputs the processed datadict to a textfile
    
        Mainly used for debugging purposes
    """
    f2 = open(f"unhw_processed.dat", "w")
    for item in datadict.items():
       print(f"{item[0]} {item[1]}", file = f2)
    f2.close()

def fit_model(datadict):
    """Fits harmonic model to tides using pytides
    """

    t = []
    heights = []
    for dt, height in datadict.items():
        #print(line.split()[:2])
        t.append(datetime.strptime(dt, "%Y-%m-%d %H:%M:%S"))
        heights.append(float(height))

    ##Fit the tidal data to the harmonic model using Pytides
    print("Fitting harmonic model")
    my_tide = Tide.decompose(np.array(heights), np.array(t))
    return my_tide

def output_html(my_tide, month, year):
    """ Dumps a html page of a calendar month of tide predictions
        todo: generalise
    """
    ##Prepare our variables for the template
    location = "Lyttelton, NZ"
    tzname = "Pacific/Auckland"
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
    env = Environment(loader=FileSystemLoader(""),trim_blocks=True)
    template = env.get_template('template.html')
    with open("output.html", "w") as fh:
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

    datadict = process_unhw_data()
    plot_data(datadict)
    my_tides = fit_model(datadict)
    print(my_tides)
    output_html(my_tides, 9, 2019)
