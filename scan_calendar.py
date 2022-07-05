#!/usr/bin/env python

from click import pass_context
from ics import Event, Calendar, ContentLine
import logging
#from tenable.io import TenableIO
from tenable.sc import TenableSC
from decouple import config, UndefinedValueError


import os

from pprint import pprint

import lib.auth
import lib.common
import lib.sc


#logging.basicConfig(level=logging.CRITICAL)

# Let's initialize the calendar before anything else
c = Calendar()

# Check local configuration to see what to do
io_configured = False
sc_configured = False
nessus_configured = False

try:
    if config('IO_URL'):
        io_configured = True
        print("io in env")
except UndefinedValueError as err: 
    pass
try:
    if config('SC_ADDRESS'):
        sc_configured = True
        print("SC in env")
except UndefinedValueError as err: 
    pass
try:
    if config('NESSUS_ADDRESS'):
        nessus_configured = True
        print('nessus in env')
except UndefinedValueError as err: 
    pass

debug_set = config('DEBUG', cast=bool, default=False)

# Debugging bit
if debug_set is True:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.CRITICAL)


####################

if io_configured:
    io_address = config('IO_URL', default="https://cloud.tenable.com")
    io_access_key = config('IO_ACCESS_KEY', default="123e4567-e89b-12d3-a456-426614174000")
    io_secret_key = config('IO_SECRET_KEY', default="123e4567-e89b-12d3-a456-426614174000")
    print('IO Configured')

if sc_configured:
    sc_address = config('SC_ADDRESS', default="https://127.0.0.1")
    sc_access_key = config('SC_ACCESS_KEY', default="123e4567-e89b-12d3-a456-426614174000")
    sc_secret_key = config('SC_SECRET_KEY', default="123e4567-e89b-12d3-a456-426614174000")
    sc_port = config('SC_PORT', default=443)
    print('SC Configured')
    sc = lib.auth.tsc_login(sc_address, sc_access_key, sc_secret_key, sc_port)
    c.events = lib.sc.sc_parse(sc, c)


if nessus_configured:
    nessus_address = config('NESSUS_ADDRESS', default="https://127.0.0.1")
    nessus_access_key = config('NESSUS_ACCESS_KEY', default="123e4567-e89b-12d3-a456-426614174000")
    nessus_secret_key = config('NESSUS_SECRET_KEY', default="123e4567-e89b-12d3-a456-426614174000")
    nessus_port = config('NESSUS_PORT', default=8834)
    print('Nessus Configured')


# Write out the calendar file
with open('tenable_scans.ics', 'w') as my_file:
    my_file.writelines(c)

'''
elif scan.get('type') == "agent":
            scan_type = "Agent"
            scan_editor_id_path = "editor/scan/" + '{id}'.format(**scan)
            scan_details_resp = sc.get(scan_editor_id_path)
            scan_details = scan_details_resp.json().get('settings').get('basic').get('inputs')
            for item in scan_details:
                if item.get('id') == "scan_time_window":
                    scan_window_time = item.get('default')
            endtime = (scan_window_time * 60)
            endtime_utc = convert_unix_time(int(starttime_utc_dt.timestamp()) + endtime)
            estimated_run = False
            
'''