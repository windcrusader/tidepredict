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
    #todo need to make this generic for a particular day and minimal
    #output.
    args = __main__.parser.parse_args(["-l","Lyttelton"])
    output = "\n".join(["All times in TZ: Pacific/Auckland",
                       "2019-09-08 0558  0.59 Low Tide",
                       "2019-09-08 1211  2.40 High Tide",
                       "2019-09-08 1835  0.64 Low Tide",
                        "2019-09-09 0034  2.26 High Tide",
                        "2019-09-09 0651  0.63 Low Tide",
                        "2019-09-09 1303  2.36 High Tide",
                        "2019-09-09 1926  0.66 Low Tide",
                        "2019-09-10 0126  2.22 High Tide",
                        "2019-09-10 0741  0.66 Low Tide",
                        "2019-09-10 1353  2.33 High Tide",
                        "2019-09-10 2015  0.67 Low Tide"]) + "\n"
    assert __main__.process_args(args) == output, "predictions don't match"


