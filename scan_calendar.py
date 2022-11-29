"""Main program for tenb_scan_calendar."""
# !/usr/bin/env python

from ics import Calendar
import logging
from decouple import config, UndefinedValueError
from lib import tenb_auth, tenb_common, tsc, tio, nessus


# Debugging bit
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(module)s %(filename)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

debug_set = config('DEBUG', cast=bool, default=False)

if debug_set is True:
    logging.basicConfig(
        level=logging.DEBUG,
        force=True,
        format='%(asctime)s %(levelname)s %(module)s %(filename)s: \
            %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

# Let's initialize the calendar before anything else
c = Calendar()

# Check local configuration to see what to do
io_configured = False
sc_configured = False
nessus_configured = False
docker_configured = False

try:
    if config('IO_URL'):
        io_configured = True
except UndefinedValueError as err:
    pass
try:
    if config('SC_ADDRESS'):
        sc_configured = True
except UndefinedValueError as err:
    pass
try:
    if config('NESSUS_URL'):
        nessus_configured = True
except UndefinedValueError as err:
    pass
try:
    if config('IS_TENB_SCAN_CALENDAR_DOCKER'):
        docker_configured = True
except UndefinedValueError as err:
    pass

####################

if io_configured:
    logging.debug('Tenable.io Configured')
    io_address = config('IO_URL', default="https://cloud.tenable.com")
    io_access_key = config('IO_ACCESS_KEY',
                           default="123e4567-e89b-12d3-a456-426614174000")
    io_secret_key = config('IO_SECRET_KEY',
                           default="123e4567-e89b-12d3-a456-426614174000")
    logging.debug('Testing Tenable.io Connection...')
    io = tenb_auth.tio_login(io_address, io_access_key, io_secret_key)
    logging.info('Validated Tenable.io Connection, pulling scan data')
    c.events = tio.io_parse(io, c)

if sc_configured:
    logging.debug('Tenable.sc Configured')
    sc_address = config('SC_ADDRESS', default="https://127.0.0.1")
    sc_access_key = config('SC_ACCESS_KEY',
                           default="123e4567-e89b-12d3-a456-426614174000")
    sc_secret_key = config('SC_SECRET_KEY',
                           default="123e4567-e89b-12d3-a456-426614174000")
    sc_port = config('SC_PORT', default=443)
    logging.debug('Testing Tenable.sc Connection...')
    sc = tenb_auth.tsc_login(sc_address, sc_access_key, sc_secret_key, sc_port)
    logging.info('Validated Tenable.sc Connection, pulling scan data')
    c.events = tsc.sc_parse(sc, c)

if nessus_configured:
    logging.debug('Tenable Nessus Configured')
    nessus_address = config('NESSUS_URL', default="https://127.0.0.1")
    nessus_access_key = config('NESSUS_ACCESS_KEY',
                               default="123e4567-e89b-12d3-a456-426614174000")
    nessus_secret_key = config('NESSUS_SECRET_KEY',
                               default="123e4567-e89b-12d3-a456-426614174000")
    nessus_port = config('NESSUS_PORT', default=8834)
    logging.debug('Testing Nessus Connection...')
    tnessus = tenb_auth.nessus_login(nessus_address, nessus_access_key,
                                     nessus_secret_key, nessus_port)
    logging.info('Validated Nessus Connection, pulling scan data')
    c.events = nessus.nessus_parse(tnessus, c)

# try to remove deleted events
try:
    existing_events = []
    tenb_ics_file = open("tenable_scans.ics", 'r')
    for line in tenb_ics_file:
        if "UID:" in line:
            existing_events.append(line[4:].strip('\n'))
    tenb_ics_file.close()
except Exception as e:
    pass

current_events = []
for event in c.events:
    current_events.append(event.uid)

for uuid in existing_events:
    if uuid not in current_events:
        e = {}
        e['uuid'] = uuid
        c.events.append(tenb_common.del_event(e))

# Write out the calendar file
if c:
    if docker_configured:
        with open('output/tenable_scans.ics', 'w') as my_file:
            my_file.writelines(c)
    else:
        with open('tenable_scans.ics', 'w') as my_file:
            my_file.writelines(c)
    logging.info('Calendar .ics file written to tenable_scans.ics')
