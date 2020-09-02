# tidepredict

A Python module for forecasting tides.

## Description

I wrote this module as I wanted a pure Python solution written to work
with my weather station which use the [WeeWX](http:http://www.weewx.com) Python codebase. WeeWX currently
uses [XTide](https://flaterco.com/xtide/), which is a fine application, but currently only has updated
harmonics constituents for US locations. I wanted a tool that could easily 
generate new harmonic constituents from a set of tidal measurements for locations outside the US.

The module is essentially a wrapper on the [pytides](https://github.com/sam-cox/pytides) module and uses
this codebase essentially unmodified to generate the harmonic constituents.

In keeping with good standards I've tried to maintain the command line interface options and 
output options of XTide. At present there is much to do and this module currently only supports the plain and list modes for output.

Currently the possible locations are limited to the
University of Hawaii's Research Quality Dataset:
[https://uhslc.soest.hawaii.edu]. 

If you run the tool with the option `-harmgen` it will automatically pull down the most recent two years of hourly measurements from the server and generate the harmonic constituents for the location.
After running this once, the constituents are saved locally and you don't need to do this again; unless you want updated data.

## Installation

```
pip install tidepredict
```

## Usage

### Example 1
```
python tidepredict -l Lyttelton
```
Should produce a series of tide predictions similar to the following:
```
Tide forecast for Lyttelton, New Zealand
Latitude:-43.60 Longitude:172.72
All times in TZ: Pacific/Auckland
2019-09-14 2259  0.63 Low Tide
2019-09-15 0502  2.18 High Tide
2019-09-15 1112  0.68 Low Tide
2019-09-15 1721  2.22 High Tide
2019-09-15 2338  0.64 Low Tide
2019-09-16 0544  2.17 High Tide
2019-09-16 1152  0.71 Low Tide
2019-09-16 1804  2.20 High Tide
2019-09-17 0018  0.66 Low Tide
2019-09-17 0628  2.16 High Tide
2019-09-17 1234  0.74 Low Tide
2019-09-17 1849  2.17 High Tide
```
the default is for three days from the current date and time. However you can add start and end times and dates using the `-e` and `-b` options.

 ### Example 2
```
python tidepredict -l Lyttelton -b 2019-11-02 00:00 -e 2019-11-03 00:00
```
```
Tide forecast for Lyttelton, New Zealand
Latitude:-43.60 Longitude:172.72
All times in TZ: Pacific/Auckland
2019-11-02 0309  0.53 Low Tide
2019-11-02 0929  2.54 High Tide
2019-11-02 1548  0.59 Low Tide
2019-11-02 2154  2.34 High Tide
```

 ### Example 3
```
python tidepredict -l Lyttelton -harmgen
```
This will search the research quality dataset for the hourly sea level measurements and generate harmonics constituents for them.

### Example 4
```
python tidepredict -l Lyttelton -fp
```
Create a tide graph using Python pandas. This is saved to the user
home directory / .tidepredict / tidegraph.png

### Example 5
```
python tidepredict -l Lyttelton -fc
```
CSV output
```
Lyttelton,2020-09-02,2259,Pacific/Auckland, 0.56, Low Tide
Lyttelton,2020-09-03,0459,Pacific/Auckland, 2.25, High Tide
Lyttelton,2020-09-03,1112,Pacific/Auckland, 0.61, Low Tide
Lyttelton,2020-09-03,1720,Pacific/Auckland, 2.32, High Tide
Lyttelton,2020-09-03,2340,Pacific/Auckland, 0.58, Low Tide
Lyttelton,2020-09-04,0542,Pacific/Auckland, 2.22, High Tide
Lyttelton,2020-09-04,1155,Pacific/Auckland, 0.64, Low Tide
Lyttelton,2020-09-04,1804,Pacific/Auckland, 2.26, High Tide
Lyttelton,2020-09-05,0022,Pacific/Auckland, 0.61, Low Tide
Lyttelton,2020-09-05,0628,Pacific/Auckland, 2.19, High Tide
Lyttelton,2020-09-05,1238,Pacific/Auckland, 0.68, Low Tide
Lyttelton,2020-09-05,1849,Pacific/Auckland, 2.21, High Tide
```


## License
MIT






