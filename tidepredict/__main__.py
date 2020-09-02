"""Main routine for managing the program
"""
from __future__ import print_function
import numpy as np
import sys
import argparse
from tidepredict import (processdata, process_station_list, constants,
constituent, process_station_info, plotpng, timefunc)
from tidepredict.tide import Tide
import pandas as pd
import json
import datetime
import timezonefinder
import pathlib

__version__ = "0.4.0"

#Setup command line arguments below. Should be self-explanatory
parser = argparse.ArgumentParser(description=
                                'tidepredict: a tide prediction module.')
parser.add_argument('-genharm',
                    action="store_true",
                    help="""Generic harmonics constants from University of 
                            Hawaii research quality data""")
parser.add_argument('-m',
                    action="store",
                    help="""Mode:
                            Specify mode to be about, banner, calendar,
                            alt. calendar, graph, clock,
                            list, medium rare, plain, raw, or stats.
                            The default is plain.""",
                    default = "p",
                    choices=['a', 'b', 'c', 'C','g', 'k', 'l', 'm', 'p',
                            'r', 's'])

parser.add_argument('-f',
                    action="store",
                    help="""Mode:
                            Specify format to be csv, html, PNG, text, or
                            SVG.
                            The default is text.""",
                    default = "t",
                    choices=['c', 'h', 'p', 't','v'])

parser.add_argument('-l',
                    action="store",
                    help="""Location to search the database for or to
                            generate harmonic constituents for.""",
                    metavar="Location")  

parser.add_argument('-r',
                    action="store_true",
                    help="""Force refresh of station database""")  

parser.add_argument('-b',
                    action="store",
                    help = "Start time to begin predictions",
                    metavar = "YYYY-MM-DD HH:MM")

parser.add_argument('-e',
                    action="store",
                    help = "end time for predictions",
                    metavar = "YYYY-MM-DD HH:MM")

    #todo add the rest of the xtide arguments once I've implemented the above
    # correctly.   

def process_args(args):

    #check we got at least one of location or list
    if args.l == None and args.m != "l":
        parser.error('Must enter a location or use list option [-m l]')

    #First try to read in the location list
    try:
        stations = pd.read_csv(constants.STATIONFILE)
        if args.r:
            #force refresh of stations if command line arg is forced
            raise EnvironmentError
    except EnvironmentError:
        #Not found then create it.
        print("Refreshing stations list from online source.")
        stations = process_station_list.create_station_dataframe()

    #Run some checks on the requested station
    if args.l != None:    #extract station data from stations df
        thestation = stations[stations.loc_name.str.contains(args.l)]
        #print(thestation)
        if thestation.empty:
            print("Station not found")
            sys.exit()
        if len(thestation) > 1:
            print("Station name ambiguous, the following stations were found:")
            print(thestation)
            sys.exit()

        loc_code = "h" + thestation.stat_idx.tolist()[0].lower()
        station_dict, harmfileloc = process_station_list.read_station_info_file()

        if args.genharm is True:
            #get the last two years that data exists for
            lastyear = int(thestation.data_years.tolist()[0][-2:])
            years = list(range(lastyear-1,lastyear+1))
            #create data url
            ocean = constants.ocean_dict[thestation.oc_idx.tolist()[0][0]]
            ftpurl = processdata.get_data_url(ocean = ocean)
            datadict = processdata.process_unhw_data(ftpurl = ftpurl,
                                                    years=years,
                                                    loc_code = loc_code)

            my_tides = processdata.fit_model(datadict)

            #get QA doc, returns a dict of dicts
            process_station_info.get_station_info(loc_code, ocean, station_dict)
            #set location data version for compatibility
            station_dict[loc_code]['version'] = __version__
            lat, lon = process_station_info.deg_2_decimal(thestation.Lat.tolist()[0],
                                            thestation.Lon.tolist()[0])  
            #write out the rest of the station information                                 
            station_dict[loc_code]['lat'] = lat
            station_dict[loc_code]['lon'] = lon
            tf = timezonefinder.TimezoneFinder(in_memory=True)
            station_dict[loc_code]['tzone'] = tf.timezone_at(lng=lon, lat=lat)
            station_dict[loc_code]['name'] = thestation.loc_name.tolist()[0]
            station_dict[loc_code]['country'] = thestation.country.tolist()[0]
            station_dict[loc_code]['contributor'] = thestation.Contributor.tolist()[0]
            station_dict[loc_code]['cons'] = [item.name for 
                                            item in my_tides.model['constituent']]
            station_dict[loc_code]['amps'] = my_tides.model['amplitude'].tolist()
            station_dict[loc_code]['phase'] = my_tides.model['phase'].tolist()
            
            #if not constants.SAVEHARMLOCATION.exists():
            #    constants.SAVEHARMLOCATION.mkdir()
            #write to file.
            harmfileloc.write_text(json.dumps(station_dict))
    
        #Try to get the saved harmonics constants from file.
        #Tide prediction using pre-generated constants is much faster than 
        #having to derive them again.
        station_dict = json.loads(harmfileloc.read_text())
        #Reconstruct tide model from saved harmonics data
        tide = processdata.reconstruct_tide_model(station_dict, loc_code)
        #print (tide.at([datetime(2019,1,1,0,0,0), datetime(2019,1,1,6,0,0)]))
        if tide is None:
            print("Harmonics data not found for %s" %args.l)
            print("Use option -genharm to generate harmonics for this location")
            sys.exit()

        #process start and end time arguments
        #check validity of start time
        timeobj = timefunc.Tidetime(st_time = args.b,
                                    en_time = args.e,
                                    station_tz = station_dict[loc_code]['tzone'])
        
    
    #output tide predictions depending on options specified.
    if args.m == "p" and (args.f == "t" or args.f == "c"):
        #Text output
        predictions = processdata.predict_plain(tide,
                                                station_dict[loc_code],
                                                args.f,
                                                timeobj)
        print(predictions)
        return predictions   

    elif args.m == "l":
        #list all available stations name and country
        for name, country, lat, lon in zip(stations['loc_name'], 
                                stations['country'],
                                stations['Lat'],
                                stations['Lon']):
            print("%18s %16s %8s %8s"%(name, country, lat, lon))

    if args.f == "p":
        #PNG output
        png = plotpng.Plotpng(tide,
                      station_dict[loc_code],
                      args.f,
                      timeobj)
    
if __name__ == "__main__":
    args = parser.parse_args()
    #print(args.harmgen)
    process_args(args)
