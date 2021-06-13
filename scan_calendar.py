#!/usr/bin/env python

from ics import Event, Calendar
from ics.parse import ContentLine
import logging
from tenable.io import TenableIO
from decouple import config, UndefinedValueError
from datetime import datetime
import pytz

#logging.basicConfig(level=logging.CRITICAL)

# Set some variables that need setting (pulled from .env file passed to container or seen locally in the same folder as script)
try:
    tio_address = config('TIO_ADDRESS', default="https://cloud.tenable.com")
    tio_access_key = config('TIO_ACCESS_KEY')
    tio_secret_key = config('TIO_SECRET_KEY')
    debug_set = config('DEBUG', cast=bool, default=False)
except UndefinedValueError as err:
    print("Please review the documentation and define the required connection details in an environment file.")
    print()
    raise SystemExit(err)

# Debugging bit
if debug_set is True:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.CRITICAL)

# Let's initialize the calendar before anything else
c = Calendar()

# Try to login to T.io
tio = TenableIO(tio_access_key, tio_secret_key)

# Define Functions
def get_timezone(tz_str):
    return pytz.timezone(tz_str)

def is_dst(tz, datetime_to_check):
    """Determine whether or not Daylight Savings Time (DST)
    is currently in effect. From 
    https://gist.github.com/dpapathanasiou/09bd2885813038d7d3eb"""

    # Jan 1 of this year, when all tz assumed to not be in dst
    non_dst = datetime(year=datetime.now().year, month=1, day=1)
    # Make time zone aware based on tz passed in
    non_dst_tz_aware = pytz.timezone(tz).localize(non_dst)

    # if DST is in effect, their offsets will be different
    return not (non_dst_tz_aware.utcoffset() == datetime_to_check.utcoffset())

def convert_dt_obj(dt):
    return datetime.strptime(dt, "%Y%m%dT%H%M%S")

def local_datetime(dt, tz, dst):
    return tz.localize(dt, is_dst=dst)

def dt_to_utc(local_dt):
    return local_dt.astimezone(pytz.utc)

def convert_unix_time(time):
    return datetime.utcfromtimestamp(time).strftime('%Y%m%dT%H%M%S')

def gen_event(name, rrules, starttime, timezone, creation_date):
    # intialize a new event
    e = Event()

    # Set the event name
    e.name = name

    # Set the start time
    tz_start = str("DTSTART;TZID=" + timezone)
    start_time_content = ContentLine(name=tz_start, params={}, value=starttime)
    e.extra.append(start_time_content)
    #e.begin = starttime

    # Set the schedule, if it exists
    if "FREQ=ONETIME" not in rrules:
        rrule_content = ContentLine(name='RRULE', params={}, value=rrules)
        e.extra.append(rrule_content)
 
    dtstamp_set = convert_unix_time(creation_date)
    dtstamp_content = ContentLine(name='DTSTAMP', params={}, value=dtstamp_set)
    e.extra.append(dtstamp_content)

    # Set the timezone in multiple places cause of different silly implementations
    #tzid_content = ContentLine(name='TZID', params={}, value=timezone)
    #e.extra.append(tzid_content)
    #x_wr_timezone_content = ContentLine(name='X-WR-TIMEZONE', params={}, value=timezone)
    #e.extra.append(x_wr_timezone_content)
    #x_lic_location_content = ContentLine(name='X-LIC-LOCATION', params={}, value=timezone)
    #e.extra.append(x_lic_location_content)
    
    # add all to events
    print(e)
    c.events.add(e)

# All the actual processing goes here
for scan in tio.scans.list():
    if '{enabled}'.format(**scan) == "True":
        tz_format = get_timezone('{timezone}'.format(**scan))
        dst = is_dst('{timezone}'.format(**scan), convert_dt_obj('{starttime}'.format(**scan)))
        starttime_utc = dt_to_utc(local_datetime(convert_dt_obj('{starttime}'.format(**scan)), tz_format, dst))
        
        print(tz_format)
        print(dst)
        print('{starttime}'.format(**scan))
        print(starttime_utc)
        
        gen_event(
                '{name}'.format(**scan), \
                '{rrules}'.format(**scan), \
                '{starttime}'.format(**scan), \
                '{timezone}'.format(**scan), \
                int('{creation_date}'.format(**scan))
                )
        #print('{name}: {id}/{uuid} - {rrules} - {starttime} - {timezone}'.format(**scan))
        print(scan)

# Put all the events into the 'calendar'
c.events

# Write out the calendar file
with open('tenableio_scans.ics', 'w') as my_file:
    my_file.writelines(c)
