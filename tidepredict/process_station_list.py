"""
module to grab the list of stations from the UN Hawaii server and check
if the user specified string can be matched to a station
"""
from tidepredict import ftp_helpers
import pandas as pd
from io import StringIO

def get_station_files():
    """Get bytes IO objects from each of the station list files
    """
    ftpurl = "ftp.soest.hawaii.edu"
    pacific = ftp_helpers.get_byte_stream(ftpurl,"uhslc/rqds/pacific/pacific.lst")
    indian = ftp_helpers.get_byte_stream(ftpurl,"uhslc/rqds/indian/indian.lst")
    atlantic = ftp_helpers.get_byte_stream(ftpurl,"uhslc/rqds/atlantic/atlantic.lst")

    return pacific, indian, atlantic

def create_station_dataframe():
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
    #todo this should go in user home.
    #todo option to force refresh of this.
    stat_df.to_csv("stations.csv")
    

    

    

