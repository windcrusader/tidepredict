from tidepredict import constants, ftp_helpers
import re

def get_station_info(loc_code, ocean, station_dict):
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
    #print(type(station_dict)
    station_dict[loc_code] = {"meridian":meridian}

def deg_2_decimal(latitude, longitude):
    """Converts degrees minutes and seconds into decimal degrees

    The inputs are strings of the form
    dd-mmH (lat) ddd-mmH (lon)
    where:
    dd is the decimal degrees
    mm is the minutes
    H is the hemisphere N/S/E/W
    """
    assert len(latitude) == 6, "Latitude is not the expected width of 6"
    assert len(longitude) == 7, "Longitude is not the expected width of 7"
    latdec = float(latitude[:2]) + float(latitude[-3:-1])/60
    #check for N/S
    if latitude[-1] == "N":
        pass
    else:
        latdec = latdec * -1
    londec = float(longitude[:3]) + float(longitude[-3:-1])/60
    #check for N/S
    if longitude[-1] == "E":
        pass
    else:
        londec = londec * -1
    return latdec, londec
    

