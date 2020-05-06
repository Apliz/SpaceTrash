##
## SLTrack.py
## (c) 2019 Andrew Stokes  All Rights Reserved
##
##
## Simple Python app to extract Starlink satellite history data from www.space-track.org into a spreadsheet
## (Note action for you in the code below, to set up a config file with your access and output details)
##
##
##  Copyright Notice:
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  For full licencing terms, please refer to the GNU General Public License
##  (gpl-3_0.txt) distributed with this release, or see
##  http://www.gnu.org/licenses/.
##

import psycopg2
import requests
import csv
import json
import configparser
import xlsxwriter
import time
from datetime import datetime
from orbital_decay.models import Orbit

class MyError(Exception):
    def __init___(self, args):
        Exception.__init__(
            self, "my exception was raised with arguments {0}".format(args))
        self.args = args

# See https://www.space-track.org/documentation for details on REST queries
# the "Find Starlinks" query searches all satellites with NORAD_CAT_ID > 40000, with OBJECT_NAME matching STARLINK*, 1 line per sat
# the "OMM Starlink" query gets all Orbital Mean-Elements Messages (OMM) for a specific NORAD_CAT_ID in JSON format


uriBase = "https://www.space-track.org"
requestLogin = "/ajaxauth/login"
requestCmdAction = "/basicspacedata/query"
requestCatalogue = "/class/tle_latest/ORDINAL/1/EPOCH/>now-30/MEAN_MOTION/>11.25/format/csv"

# Parameters to derive apoapsis and periapsis from mean motion (see https://en.wikipedia.org/wiki/Mean_motion)

GM = 398600441800000.0
GM13 = GM ** (1.0/3.0)
MRAD = 6378.137
PI = 3.14159265358979
TPI86 = 2.0 * PI / 86400.0

# ACTION REQUIRED FOR YOU:
#=========================
# Provide a config file in the same directory as this file, called SLTrack.ini, with this format (without the # signs)
# [configuration]
# username = XXX
# password = YYY
# output = ZZZ
#
# ... where XXX and YYY are your www.space-track.org credentials (https://www.space-track.org/auth/createAccount for free account)
# ... and ZZZ is your Excel Output file - e.g. starlink-track.xlsx (note: make it an .xlsx file)

# Use configparser package to pull in the ini file (pip install configparser)
config = configparser.ConfigParser()
config.read("./API/SLTrack.ini")
configUsr = config.get("configuration", "username")
configPwd = config.get("configuration", "password")
siteCred = {'identity': configUsr, 'password': configPwd}

# use requests package to drive the RESTful session with space-track.org
with requests.Session() as session:
    # run the session in a with block to force session to close if we exit
    print("Starting API request.....")
    # need to log in first. note that we get a 200 to say the web site got the data, not that we are logged in
    resp = session.post(uriBase + requestLogin, data=siteCred)
    if resp.status_code != 200:
        raise MyError(resp, "POST fail on login")

    # this query picks up all Starlink satellites from the catalog. Note - a 401 failure shows you have bad credentials
    resp = session.get(uriBase + requestCmdAction + requestCatalogue)
    if resp.status_code != 200:
        print(resp)
        raise MyError(resp, "GET fail on request for Starlink satellites")

    for sat in resp.content:
        orbit = Orbit(
            ORDINAL = sat['ORDINAL'],
            COMMENT = sat['COMMENT'],
            ORIGINATOR = sat['ORIGINATOR'],
            NORAD_CAT_ID = sat['NORAD_CAT_ID'],
            OBJECT_NAME = sat['OBJECT_NAME'],
            OBJECT_TYPE = sat['OBJECT_TYPE'],
            CLASSIFICATION_TYPE = sat['CLASSIFICATION_TYPE'],
            INTLDES = sat['INTLDES'],
            EPOCH = sat['EPOCH'],
            EPOCH_MICROSECONDS = sat['EPOCH_MICROSECONDS'],
            MEAN_MOTION = sat['MEAN_MOTION'],
            ECCENTRICITY = sat['ECCENTRICITY'],
            INCLINATION = sat['INCLINATION'],
            RA_OF_ASC_NODE = sat['RA_OF_ASC_NODE'],
            ARG_OF_PERICENTER = sat['ARG_OF_PERICENTER'],
            MEAN_ANOMALY = sat['MEAN_ANOMALY'],
            EPHEMERIS_TYPE = sat['EPHEMERIS_TYPE'],
            ELEMENT_SET_NO = sat['ELEMENT_SET_NO'],
            REV_AT_EPOCH = sat['REV_AT_EPOCH'],
            BSTAR = sat['BSTAR'],
            MEAN_MOTION_DOT = sat['MEAN_MOTION_DOT'],
            MEAN_MOTION_DDOT = sat['MEAN_MOTION_DDOT'],
            FILE = sat['FILE'],
            TLE_LINE0 = sat['TLE_LINE0'],
            TLE_LINE1 = sat['TLE_LINE1'],
            TLE_LINE2 = sat['TLE_LINE2'],
            OBJECT_ID = sat['OBJECT_ID'],
            OBJECT_NUMBER = sat['OBJECT_NUMBER'],
            SEMIMAJOR_AXIS = sat['SEMIMAJOR_AXIS'],
            PERIOD = sat['PERIOD'],
            APOGEE = sat['APOGEE'],
            PERIGEE = sat['PERIGEE'],
            DECAYED = sat['DECAYED'],
        )
        orbit.save()


    # f = open('api_data.csv', "w")
    # f.write(resp.text)
    # f.close()

    session.close()

print("Completed API session.....")
print("Writing Data to Database.....")

# conn = psycopg2.connect("host=localhost dbname=sat_data")
# cur = conn.cursor()
# with open('api_data.csv', 'r') as f:
#     # Notice that we don't need the `csv` module.
#     next(f) # Skip the header row.
#     cur.copy_from(f, 'orbits', sep=',')

# conn.commit()

print("Complete")
