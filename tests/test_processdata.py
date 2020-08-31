from tidepredict import processdata
import pytest
from tidepredict import ftp_helpers
from tidepredict import __main__
import argparse
from tidepredict import process_station_info
from tidepredict import timefunc
import pytz
import datetime

def test_time():
    fmt = "%Y-%m-%d %H:%M"
    timeobj = timefunc.Tidetime(st_time = "2019-10-02 13:00",
                                en_time = "2019-10-03 16:00",
                                station_tz = "Pacific/Auckland")

    assert timeobj.st_utc.strftime(fmt) == "2019-10-02 00:00"
    assert timeobj.en_utc.strftime(fmt) == "2019-10-03 03:00"

        
    


def test_get_data_url():
    assert processdata.get_data_url("indian") == "uhslc/rqds/indian"
    assert processdata.get_data_url("pacific") == "uhslc/rqds/pacific"
    assert processdata.get_data_url("atlantic") == "uhslc/rqds/atlantic"
    with pytest.raises(Exception):
        processdata.get_data_url("")

def test_get_byte_stream():
    data = ftp_helpers.get_byte_stream("ftp.soest.hawaii.edu",
                                        "uhslc/rqds/pacific/pacific.lst") 
    data = data.read()

def test_prediction_p():
    args = __main__.parser.parse_args(["-l","Lyttelton",
                                        "-b", "2019-10-01 00:00",
                                        "-e", "2019-10-01 08:00"])
    output = "\n".join(["Tide forecast for Lyttelton, New Zealand",
                        "Latitude:-43.60 Longitude:172.72",
                       "2019-10-01 0050 Pacific/Auckland 0.23 Low Tide",
                       "2019-10-01 0702 Pacific/Auckland 2.64 High Tide"]) + "\n"
    assert __main__.process_args(args) == output

def test_prediction_pc():
    args = __main__.parser.parse_args(["-l","Lyttelton",
                                        "-b", "2019-10-01 00:00",
                                        "-e", "2019-10-01 08:00",
                                        "-fc"])
    output = "\n".join([
                "Lyttelton,2019-10-01,0050,Pacific/Auckland, 0.23, Low Tide",
                "Lyttelton,2019-10-01,0702,Pacific/Auckland, 2.64, High Tide"]) + "\n"
    assert __main__.process_args(args) == output    

def test_deg_2_dec():
    assert process_station_info.deg_2_decimal("02-45N", "072-21E") == (2.75, 72.35)
    assert process_station_info.deg_2_decimal("02-45S", "072-21W") == (-2.75, -72.35)


