"""Main routine for managing the program
"""
import sys
import argparse
from tidepredict import processdata
from tidepredict import process_station_list
from tidepredict import constants
import os
import pandas as pd
import jsonpickle

def process_args(args):
    #First try to read in the location list
    try:
        stations = pd.read_csv(constants.stationfile)
        if args.r:
            #force refresh of stations if command line arg is forced
            raise FileNotFoundError
    except FileNotFoundError:
        #Not found then create it.
        stations = process_station_list.create_station_dataframe()

    #extract station data from stations df
    thestation = stations[stations.loc_name == args.l]
    print(thestation)
    
    if thestation.empty:
        raise Exception("Station not found")

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
        jpic = jsonpickle.dumps(my_tides)
        print(jpic, file=harmfile)
        harmfile.close()
    
    try:
        with open(os.path.join(constants.saveharmlocation,loc_code+".json"),"r") as tidemodel:
            #todo reconstruct tide model
            my_tide = jsonpickle.loads(tidemodel.read())
            print(my_tide)
            processdata.output_html(my_tide, 9, 2019)
    except FileNotFoundError:
        print("Harmonics data not found for %s" %args.l)
        print("Rerun program with option -harmgen")

    #todo check to see if station harmonics file is already existing 
    



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

 #todo add the rest of the xtide arguments once I've implemented the above
 # correctly.        

args = parser.parse_args()
#print(args.harmgen)
process_args(args)
