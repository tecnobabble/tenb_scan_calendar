
import json

import pytz
from datetime import datetime
from dateutil import parser
from ics import Event, Calendar, ContentLine

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

def return_utc(timezone,timestamp):
        tz_format = get_timezone(timezone)
        dst = is_dst(timezone, convert_dt_obj(timestamp))
        timestamp_utc_dt = local_datetime(convert_dt_obj(timestamp), tz_format, dst)
        return dt_to_utc(timestamp_utc_dt),timestamp_utc_dt

def gen_event(name, rrules, starttime, timezone, creation_date, owner, scan_type, description, uuid, scan_targets, starttime_utc, endtime_utc, estimated_run):
    # intialize a new event
    e = Event()

    # Set the event name
    e.summary = name

    # Set the uuid

    e.uid = uuid + "@schedule.invalid"

    # Set the start time
    e.begin = parser.parse(starttime_utc)

    if endtime_utc:
        e.end = parser.parse(endtime_utc)

    #e.url = "https://cloud.tenable.com"

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

    return(e)