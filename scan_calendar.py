#!/usr/bin/env python

from ics import Event, Calendar, ContentLine
import logging
#from tenable.io import TenableIO
from tenable.sc import TenableSC
from decouple import config, UndefinedValueError
from datetime import datetime
from dateutil import parser
import ast
import pytz
import os
from pprint import pprint

#logging.basicConfig(level=logging.CRITICAL)

# Set some variables that need setting (pulled from .env file passed to container or seen locally in the same folder as script)
try:
    sc_address = config('SC_ADDRESS')
    sc_access_key = config('SC_ACCESS_KEY')
    sc_secret_key = config('SC_SECRET_KEY')
    sc_port = config('SC_PORT', default=443)
    debug_set = config('DEBUG', cast=bool, default=False)
except UndefinedValueError as err:
    print("Please review the documentation and define the required connection details in an environment file.")
    print()
    raise SystemExit(err)

# Login to Tenable.sc
def tsc_login():
    try:
        sc = TenableSC(sc_address, port=sc_port, access_key=sc_access_key, secret_key=sc_secret_key, backoff=5.0, timeout=10)
    except (NameError, TimeoutError) as err:
        print("Please verify connection details.")
        exit()
    except (ConnectionError) as err:
        raise SystemExit(err)
    return sc





# Debugging bit
if debug_set is True:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.CRITICAL)

# Let's initialize the calendar before anything else
c = Calendar()

#Login to stuff

sc = tsc_login()


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
    return local_dt.astimezone(pytz.utc).strftime('%Y%m%dT%H%M%SZ')

def convert_unix_time(time):
    return datetime.utcfromtimestamp(time).strftime('%Y%m%dT%H%M%SZ')

def list_avg(lst):
    return sum(lst) / len(lst)

def gen_event(name, rrules, starttime, timezone, creation_date, owner, scan_type, description):
    # intialize a new event
    e = Event()

    # Set the event name
    e.summary = name

    # Set the start time
    e.begin = parser.parse(starttime_utc)

    if endtime_utc:
        e.end = parser.parse(endtime_utc)

    e.url = "https://cloud.tenable.com"

    if scan_type == "Agent":
        scan_length_desc = "The agent scan window has been set in the scan job."
    elif scan_type == "Network" and estimated_run is True:
        scan_length_desc = "The scan time has been estimated based on the average of the previously run jobs."
    elif scan_type == "Network" and estimated_run is False and endtime_utc:
        scan_length_desc = "The max scan time has been set in the job."
    else:
        scan_length_desc = "The duration of the calendar event for this job has defaulted to 1 hour, as we cannot yet estimate how long it will take and no max has been set."

    e.description = "Scan Owner: " + owner + "\n" + \
            "Scan Description: " + description + "\n" + \
            "Scan Type: " + scan_type + "\n" + \
            scan_targets + "\n" + \
            "Scan Length: " + scan_length_desc

    
    # Set the schedule, if it exists
    if "FREQ=ONETIME" not in rrules and rrules != "":
        rrule_content = ContentLine(name='RRULE', params={}, value=rrules)
        e.extra.append(rrule_content)
 
    dtstamp_set = convert_unix_time(creation_date)
    dtstamp_content = ContentLine(name='DTSTAMP', params={}, value=dtstamp_set)
    e.extra.append(dtstamp_content)

    # add all to events
    c.events.append(e)

# All the actual processing goes here
for scan in sc.scans.list(['id','name','schedule', 'createdTime', 'owner','maxScanTime', 'ipList', 'assets', 'description'])['manageable']:
    if '{schedule[enabled]}'.format(**scan) == "true":
        raw_timezone = '{schedule[start]}'.format(**scan).split('=')[1].split(':')[0]
        raw_start = '{schedule[start]}'.format(**scan).split('=')[1].split(':')[1]
        tz_format = get_timezone(raw_timezone)
        dst = is_dst(raw_timezone, convert_dt_obj(raw_start))
        
        starttime_utc_dt = local_datetime(convert_dt_obj(raw_start), tz_format, dst)
        starttime_utc = dt_to_utc(starttime_utc_dt)

        # We're going to have to do fun things to determine scan endtimes.
        if '{maxScanTime}'.format(**scan) != 'unlimited':
            endtime = (int('{maxScanTime}'.format(**scan)) * 60 * 60)
            endtime_utc = convert_unix_time(int(starttime_utc_dt.timestamp()) + endtime)
            estimated_run = False
            scan_type = "Network"
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
        else:
            endtime_utc = None
            estimated_run = False
            scan_type = "Network"
            '''
            # if the scan isn't a one-off, check to see if there is a history 
            # we can use to guess the time it's going to take to run.
            
            if scan.get('schedule').get('repeatRule') != "FREQ=ONETIME":
                scan_history = sc.scans.history(scan.get('id'))
                scan_duration = []
                scan_duration_count = 5
                scan_duration_iter = 0
                for past_scan in scan_history:
                    if past_scan.get('status') == "completed":
                        scan_duration.append(past_scan.get('time_end') - past_scan.get('time_start'))
                        scan_duration_iter+=1
                        if scan_duration_iter == scan_duration_count:
                            break
                endtime = list_avg(scan_duration)
                endtime_utc = convert_unix_time(int(starttime_utc_dt.timestamp()) + endtime)
                estimated_run = True
            '''


        asset_list = ""
        asset_targets = ast.literal_eval('{assets}'.format(**scan))
        if len(asset_targets) > 0:
            for x in asset_targets:
                asset_list+= x['name'] + " "
        scan_targets = "Targeted Assets: " + asset_list + "\n" + \
            "Targeted IPs: " + '{ipList}'.format(**scan)
        gen_event(
                '{name}'.format(**scan), \
                '{schedule[repeatRule]}'.format(**scan), \
                raw_start, \
                raw_timezone, \
                int('{createdTime}'.format(**scan)), \
                '{owner[username]}'.format(**scan), \
                scan_type, \
                '{description}'.format(**scan), \
                )

#for policy in tio.policies.list():
#    pprint(policy)

# Put all the events into the 'calendar'
c.events

# Write out the calendar file
with open('tenablesc_scans.ics', 'w') as my_file:
    my_file.writelines(c)
