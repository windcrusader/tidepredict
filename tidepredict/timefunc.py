
"""Helper module for for local to UTC time conversions.


"""
import datetime
import pytz
import sys
from tidepredict import constants

class Tidetime:

    def __init__(self,
                st_time = None,
                en_time = None,
                station_tz = None):

        if station_tz is not None:
            self.tz = pytz.timezone(station_tz)
        else:
            self.tz = pytz.utc
        #print(tz)
        self.utc = pytz.utc

        if st_time is not None:
            try:
                self.st_local = datetime.datetime.strptime(st_time,"%Y-%m-%d %H:%M")
                self.st_local = self.tz.localize(self.st_local)
            except ValueError:
                print("Start time format does not match expected YYYY-MM-DD HH:MM")
                sys.exit()
        else:
            self.st_local = datetime.datetime.now(self.utc) 
            self.st_local = self.st_local.astimezone(self.tz) 

        #check validity of end time
        if en_time is not None:
            try:
                self.en_local = datetime.datetime.strptime(en_time,"%Y-%m-%d %H:%M")
                self.en_local = self.tz.localize(self.en_local)
            except ValueError:
                print("End time format does not match expected YYYY-MM-DD HH:MM")
                sys.exit()
        else:
            self.en_local = self.st_local + datetime.timedelta(days=constants.TEXTSPAN)

        #convert times to utc for all calculations
        self.st_utc = self.st_local.astimezone(self.utc)
        self.en_utc = self.en_local.astimezone(self.utc) 

    def localise(self, dtime):
        time = self.tz.normalize(dtime.astimezone(self.tz))
        time = time + datetime.timedelta(minutes=time.second > 30)
        return time
    
    def localiselist(self,timelist):
        return [item.astimezone(self.tz) for item in timelist]    
        