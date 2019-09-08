from tidepredict import processdata
import pytest
from tidepredict import ftp_helpers
from tidepredict import __main__
import argparse

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

def test_prediction():
    args = __main__.parser.parse_args(["-l","Lyttelton",
                                        "-b", "2019-10-01 00:00",
                                        "-e", "2019-10-01 08:00"])
    output = "\n".join(["All times in TZ: Pacific/Auckland",
                       "2019-10-01 0050  0.23 Low Tide",
                       "2019-10-01 0702  2.64 High Tide"]) + "\n"
    assert __main__.process_args(args) == output


