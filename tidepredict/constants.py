"""
Constants used throughout the module
"""
import sys
if sys.version_info[0] < 3:
    import pathlib2 as pathlib
else:
    import pathlib

#home location
HOME = pathlib.Path.home()
#folder to store tidepredict files
SAVEFILELOCATION = HOME / ".tidepredict" 
#stations csv file
STATIONFILE = SAVEFILELOCATION / "stations.csv"
#saveharmdata location
SAVEHARMLOCATION = HOME / SAVEFILELOCATION / "harmdata"
#ocean dict
ocean_dict = {'P':"pacific","I":"indian","A":"atlantic"}
#ftp base address
FTP_BASE = "ftp.soest.hawaii.edu"
#urls to QA data
def qa_ftp(ocean):
    return "uhslc/rqds/%s/doc/" %ocean
