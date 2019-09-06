"""
Constants used throughout the module
"""
from os.path import expanduser
import os

#home location
home = expanduser("~")
#folder to store tidepredict files
savefilelocation = os.path.join(home,".tidepredict")
#stations csv file
stationfile = os.path.join(savefilelocation,"stations.csv")
#saveharmdata location
saveharmlocation = os.path.join(home, savefilelocation, "harmdata")
#ocean dict
ocean_dict = {'P':"pacific","I":"indian","A":"atlantic"}