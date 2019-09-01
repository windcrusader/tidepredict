from datetime import datetime, timedelta
import calendar
from pytides.tide import Tide
from pytz import timezone
import numpy as np
from jinja2 import Environment, FileSystemLoader

##Import our tidal data
station_id = '8516945'
heights = []
t = []
f = open("2015processed.dat", 'r')
for i, line in enumerate(f):
    #print(line.split()[:2])
    t.append(datetime.strptime(" ".join(line.split()[:2]), "%Y-%m-%d %H:%M:%S"))
    heights.append(float(line.split()[2]))
f.close()

##Fit the tidal data to the harmonic model using Pytides
my_tide = Tide.decompose(np.array(heights[::10]), np.array(t[::10]))

##Prepare our variables for the template
location = "Lyttelton, NZ"
tzname = "Pacific/Auckland"
tz = timezone(tzname)
utc = timezone('UTC')
datum = "MLLW"
units = "metres"
year = 2019
month = 9
rows = []
for day in range(1,calendar.monthrange(year,month)[1] + 1):
    start = tz.localize(datetime(year, month, day))
    end = start + timedelta(days=1)
    startUTC = utc.normalize(start.astimezone(utc))
    endUTC = utc.normalize(end.astimezone(utc))
    extremaUTC = my_tide.extrema(startUTC, endUTC)
    date = {'date': day, 'day': calendar.day_abbr[start.weekday()]}
    extrema = []
    for e in extremaUTC:
        e = list(e)
        #print(e)
        time = tz.normalize(e[0].astimezone(tz))
        ##Round the time to the nearest minute
        time = time + timedelta(minutes=time.second > 30)
        height = e[1]
        extrema.append({'time': time.strftime('%H:%M'), 'height': "{0:.2f}".format(height)})
    #This is just for nicer formatting of days with only three tides
    for _ in range(4 - len(extrema)):
        extrema.append({'time': '', 'height': ''})
    rows.append([date, extrema])

##Render our template
print(rows)
env = Environment(loader=FileSystemLoader(""),trim_blocks=True)
template = env.get_template('template.html')
with open("output.html", "wb") as fh:
    fh.write(template.render(
    location = location,
    tzname = tzname,
    datum = datum,
    units = units,
    year = year,
    month = calendar.month_name[month],
    rows = rows
    ))