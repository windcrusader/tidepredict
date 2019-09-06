"""
FTP helper functions
"""
from io import BytesIO
from ftplib import FTP

def get_byte_stream(ftpurl, ftpfile):
    """Returns a file byte stream retrieved from an FTP site"
    Input: 
        ftpfile is a string representing an internet ftp location
    """

    #check for null string
    assert ftpfile != "", "FTP string must not be empty"
    #print(ftpurl)
    ftp = FTP(ftpurl)
    ftp.login() # Username: anonymous password: anonymous@
    sio = BytesIO()
    def handle_binary(more_data):
        sio.write(more_data)
    ftpstring = "RETR /%s"%(ftpfile)
    
    print("ftp request:%s"%ftpstring)
    resp = ftp.retrbinary(ftpstring, callback=handle_binary)
    sio.seek(0) # Go back to the start
    return sio