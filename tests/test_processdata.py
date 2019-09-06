from tidepredict import processdata
import pytest
from tidepredict import ftp_helpers

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
    