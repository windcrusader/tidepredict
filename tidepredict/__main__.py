"""Main routine for managing the program
"""
from __future__ import print_function
import numpy as np
import sys
import argparse
from tidepredict import processdata
from tidepredict import process_station_list
from tidepredict import constants
from tidepredict import constituent
from tidepredict.tide import Tide
import os
import pandas as pd
import json
import datetime



parser = argparse.ArgumentParser(description=
                                'tidepredict: a tide prediction module.')
parser.add_argument('-harmgen',
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
parser.add_argument('-l',
                    action="store",
                    help="""Location to search the database for or to
                            generate harmonic constituents for.""",
                    metavar="Location",
                    required = True)  

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
    #First try to read in the location list
    try:
        stations = pd.read_csv(constants.stationfile)
        if args.r:
            #force refresh of stations if command line arg is forced
            raise EnvironmentError
    except EnvironmentError:
        #Not found then create it.
        print("Refreshing stations list from online source.")
        stations = process_station_list.create_station_dataframe()

    #extract station data from stations df
    thestation = stations[stations.loc_name == args.l]
    #print(thestation)
    
    if thestation.empty:
        print("Station not found")
        sys.exit()

    loc_code = "h" + thestation.stat_idx.tolist()[0].lower()
    if args.harmgen is True:
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
        if not os.path.exists(constants.saveharmlocation):
            os.mkdir(constants.saveharmlocation)
        harmfile = open(os.path.join(constants.saveharmlocation,loc_code+".json"), "w+")
        #print(my_tides)
        #jpic = pickle.dumps(my_tides.model)
        cons = [item.name for item in my_tides.model['constituent']]
        jpic = json.dumps([cons,my_tides.model['amplitude'].tolist(),my_tides.model['phase'].tolist()])
        #print(my_tides.model['constituents'])
        print(jpic, file=harmfile)
        harmfile.close()
    
    #Try to get the saved harmonics constants from file.
    #Tide prediction using pre-generated constants is much faster than 
    #having to derive them again.
    try:
        with open(os.path.join(constants.saveharmlocation,
                  loc_code+".json"),"r") as tidemodelfile:
            #Reconstruct tide model from saved harmonics data
            tide = processdata.reconstruct_tide_model(tidemodelfile)
            #print (tide.at([datetime(2019,1,1,0,0,0), datetime(2019,1,1,6,0,0)]))
    except FileNotFoundError:
        print("Harmonics data not found for %s" %args.l)
        print("Use option -harmgen to generate harmonics for this location")
        sys.exit()

    #check validity of start time
    if args.b is not None:
        try:
            start = datetime.datetime.strptime(args.b,"%Y-%m-%d %H:%M")
        except ValueError:
            print("Start time format does not match expected YYYY-MM-DD HH:MM")
            sys.exit()
    else:
        start = datetime.datetime.today()

    #check validity of end time
    if args.e is not None:
        try:
            end = datetime.datetime.strptime(args.e,"%Y-%m-%d %H:%M")
        except ValueError:
            print("End time format does not match expected YYYY-MM-DD HH:MM")
            sys.exit()
    else:
        end = start + datetime.timedelta(days=3)
    

    #output tide predictions
    if args.m == "p":
        predictions = processdata.predict_plain(tide,
                                                startdate=start,
                                                enddate=end)
        print(predictions)
    return predictions
    
if __name__ == "__main__":
    args = parser.parse_args()
    #print(args.harmgen)
    process_args(args)
