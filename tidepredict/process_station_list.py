"""
module to grab the list of stations from the UN Hawaii server and check
if the user specified string can be matched to a station
"""
from tidepredict import ftp_helpers
import pandas as pd
from io import StringIO
from tidepredict import constants
import json
import pathlib

def get_station_files():
    """Get bytes IO objects from each of the station list files
    """
    ftpurl = "ftp.soest.hawaii.edu"
    pacific = ftp_helpers.get_byte_stream(ftpurl,"uhslc/rqds/pacific/pacific.lst")
    indian = ftp_helpers.get_byte_stream(ftpurl,"uhslc/rqds/indian/indian.lst")
    atlantic = ftp_helpers.get_byte_stream(ftpurl,"uhslc/rqds/atlantic/atlantic.lst")

    return pacific, indian, atlantic

def create_station_dataframe():
    """Creates a pandas dataframe from the csv list of all stations
    downloaded from the uhrqds.
    """
    files = get_station_files()
    combinedlst = ""
    for item in files:
        for line in item.read().decode().splitlines():
            try:
                #Try to convert the first three letters of the line to 
                #an int, if successful then we can assume we have a 
                #station info line, so save it to the overall file.
                int(line[:3])
                combinedlst += line + "\n"
            except:
                pass
    #print(combinedlst)
    stat_df = pd.read_fwf(StringIO(combinedlst),
                          header=None,
                          names = ["stat_idx", "oc_idx", "x", "loc_name",
                                   "country", "Lat", "Lon", "data_years",
                                   "CI", "Contributor"])

    #dump to file
    if not constants.SAVEFILELOCATION:
        constants.SAVEFILELOCATION.mkdir(parents=True)
    else:
        stat_df.to_csv(constants.STATIONFILE)
    return stat_df
    
def read_station_info_file():
    """Reads the station info json file which contains downloaded and 
    processed harmonics model data for each station that has had
    -harmgen run
    """
    if not constants.SAVEHARMLOCATION.exists():
        constants.SAVEHARMLOCATION.mkdir(parents=True)

    harmfileloc = constants.SAVEHARMLOCATION / "stations_harms.json"
    if not harmfileloc.exists():
        #create the file
        harmfileloc.touch()
        adict = {}
        harmfileloc.write_text(json.dumps(adict))
    #load station harmonics data
    return json.loads(harmfileloc.read_text()), harmfileloc

def write_station_info_file(harmfileloc, stationdict):
    harmfileloc.write_text(json.dumps(stationdict))




    




    

    

