#generate PNG graph of tides

import datetime
from tidepredict.tide import Tide
from tidepredict import constants
import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pytz

mpl.rcParams['font.size'] = 8

class Plotpng():

    def __init__(self,
                tide,
                station_data,
                form,
                timeobj):
        self.tide = tide
        self.station_data = station_data
        self.format = form
        self.timeobj = timeobj

        self.get_tides()

    def get_tides(self):
        # Prepare a list of datetimes, each 6 minutes apart between start and
        # end time.
        timesutc = pd.date_range(self.timeobj.st_utc, 
                                 self.timeobj.st_utc + 
                                 datetime.timedelta(days=constants.GRAPHSPAN),
                                 freq='6min',
                                 tz="UTC")

        #print(timesutc[:5])
        mpl.rcParams['timezone'] = str(self.timeobj.tz)

        timeslocal = self.timeobj.localiselist(timesutc)
        #print(timeslocal[:5])
        #print(timeslocal)
        #Generate tide heights
        my_prediction = self.tide.at(timesutc.tolist())
        #print(my_prediction)
        df = pd.DataFrame(index=timeslocal, data = my_prediction,
                         columns = ["tide height in (m)"] )
        #print(df.head())

        #fig, ax = plt.subplots(figsize=[12,4])
        fig, ax = plt.subplots() 
        df.plot(ax=ax, legend=None)
        plt.grid(axis='y')
        #plt.tick_params(axis="y",direction="in",pad=-25)
        #plt.tick_params(axis="x",direction="in",pad=-15,)
        
        plt.title(self.station_data['name'] + ", " 
                 + self.station_data['country'] + " Timezone: " +
                 self.station_data['tzone'])
        plt.ylabel("tide height in metres")
        hours = mdates.HourLocator(interval = 1)
        h_fmt = mdates.DateFormatter('%H')
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_major_formatter(h_fmt)
        plt.fill_between(df.index,df['tide height in (m)'],
                        df['tide height in (m)'].min(), color='b', alpha=0.5)

        #plot extrema dates as text
        extremaUTC = self.tide.extrema(self.timeobj.st_utc, 
                     self.timeobj.st_utc +
                     datetime.timedelta(days=constants.GRAPHSPAN))
        #get max extent for plotting position
        #offset lower so it is always in the graph limits
        maxval = df['tide height in (m)'].max() -0.1 
        fmt = "%Y-%m-%d\n%H:%M"
        for e in extremaUTC:
        #print(e)
        #get localised time
            time = self.timeobj.localise(e[0])

            plt.text(time, maxval, time.strftime(fmt))
        #plt.margins(y=0.1)
        #plt.show()
        plt.savefig(constants.GRAPHFILE, format="svg")
        #convert datetime to timestamp using method from stackoverflow
        #answer in ms.
        df.index = df.index.values.astype(np.int64) // 10 ** 6
        df.to_csv(constants.CSVFILE, float_format='%.3f')
        print(df.head())
        #for e in self.tide.extrema(self.startdate, self.enddate):
        #    print(e)

