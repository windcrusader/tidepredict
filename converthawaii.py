from datetime import datetime
from pytides.tide import Tide
import numpy as np
import matplotlib.pyplot as plt



f = open("h667a/i667a15.dat", 'r')
format = ""
for i, line in enumerate(f):
    if i == 0:
        continue
    #print(line)
    tideheights = line.split()[3:15]
    dateraw = line.split()[2]
    dateactual = ( dateraw[:4] + "-" + dateraw[4:6] + "-" + dateraw[6:8]
                   )
    for j,item in enumerate(tideheights):
        format += dateactual 
        if dateraw[8] == "1":
            format += " %02d" %(j) + ":00:00"
        else:
            format += " %02d" %(j + 12) + ":00:00"
        format += " " +str(float(item)/1000) + "\n"
f.close()
f2 = open("2015processed.dat", "w")
print(format, file = f2)
f2.close()
