from tidepredict import processdata
import pytest

def test_get_data_url():
    assert processdata.get_data_url("indian") == "uhslc/rqds/indian"
    assert processdata.get_data_url("pacific") == "uhslc/rqds/pacific"
    assert processdata.get_data_url("atlantic") == "uhslc/rqds/atlantic"
    with pytest.raises(Exception):
        processdata.get_data_url("")
    