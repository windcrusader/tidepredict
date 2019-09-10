from tidepredict import constants, ftp_helpers
import re

def get_station_info(loc_code, ocean):
    """returns info gathered about the station from the QA file
    """
    
    qafile = ftp_helpers.get_byte_stream(constants.FTP_BASE,
                                        "uhslc/rqds/%s/doc/qa%s.dmt" %(ocean,
                                                    loc_code[1:]))
    text = qafile.read().decode()
    try:
        meridian = re.search(r"Meridian: (\w*)", text).group(1)
    except IndexError:
        print("Could not find time meridian info in qa%s.dmt" %loc_code[1:])
    return {"meridian":meridian}

