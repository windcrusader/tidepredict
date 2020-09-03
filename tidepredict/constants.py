"""
Constants used throughout the module
"""
import sys
import pathlib

#default time spans
GRAPHSPAN = 1
TEXTSPAN = 3
#home location
HOME = pathlib.Path.home()
#folder to store tidepredict files
SAVEFILELOCATION = HOME / ".tidepredict" 
#stations csv file
STATIONFILE = SAVEFILELOCATION / "stations.csv"
#saveharmdata location
SAVEHARMLOCATION = HOME / SAVEFILELOCATION / "harmdata"
#graph file
GRAPHFILE = SAVEFILELOCATION / "tidegraph.png"
#csv data
CSVFILE = SAVEFILELOCATION / "tidegraph.csv"
#ocean dict
ocean_dict = {'P':"pacific","I":"indian","A":"atlantic"}
#ftp base address
FTP_BASE = "ftp.soest.hawaii.edu"
#urls to QA data
def qa_ftp(ocean):
    return "uhslc/rqds/%s/doc/" %ocean
