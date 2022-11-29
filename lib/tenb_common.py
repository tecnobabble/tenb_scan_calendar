"""Common functions for tenb_scan_calendar."""

import json
import pytz
from datetime import datetime
from dateutil import parser
from ics import Event, ContentLine
from datetime import tzinfo
from requests import Response


def get_timezone(tz_str: str):
    """Convert a timezone string to datetime.tzinfo object.

    Args:
        tz_str (str): timezone in a string

    Returns:
        tzinfo: datetime.tzinfo object
    """
    return pytz.timezone(tz_str)


def tenb_response_parse(response: Response):
    """Parse a requests response into json.

    Args:
        response (Response): Response object from requests

    Returns:
        json: json object
    """
    try:
        return json.loads(response.text)['response']
    except KeyError:
        return json.loads(response.text)


def is_dst(tz, datetime_to_check):
    """Determine DST or not.

    Determine whether or not Daylight Savings Time (DST)
    is currently in effect. From
    https://gist.github.com/dpapathanasiou/09bd2885813038d7d3eb
    """
    # Jan 1 of this year, when all tz assumed to not be in dst
    non_dst = datetime(year=datetime.now().year, month=1, day=1)
    # Make time zone aware based on tz passed in
    non_dst_tz_aware = pytz.timezone(tz).localize(non_dst)

    # if DST is in effect, their offsets will be different
    return not (non_dst_tz_aware.utcoffset() == datetime_to_check.utcoffset())


def convert_dt_obj(dt: str):
    """Convert date string to datetime object.

    Args:
        dt (str): datetime string in %Y%m%dT%H%M%S

    Returns:
        datetime: datetime object
    """
    return datetime.strptime(dt, "%Y%m%dT%H%M%S")


def local_datetime(dt: datetime, tz: tzinfo, dst: bool):
    """Return proper datetime if in DST in given Timezone.

    Args:
        dt (datetime): datetime object
        tz (tzinfo): datetime timezone object
        dst (bool): Observing DST yes or no

    Returns:
        datetime: localized datetime based on TZ and DST
    """
    return tz.localize(dt, is_dst=dst)


def dt_to_utc(local_dt: datetime):
    """Convert local timezone datetime object to UTC datetime object.

    Args:
        local_dt (datetime): datetime based on local timezone

    Returns:
        datetime: datetime based on utc
    """
    return local_dt.astimezone(pytz.utc).strftime('%Y%m%dT%H%M%SZ')


def convert_unix_time(time: str):
    """Convert Unix Time str to datetime object.

    Args:
        time (str): unixtime string

    Returns:
        Event: iCalendar Event object
    """
    return datetime.utcfromtimestamp(time).strftime('%Y%m%dT%H%M%SZ')


def list_avg(lst: list):
    """Return average of integers in a list.

    Args:
        lst (list): a list object of numbers

    Returns:
        int: average of the items in the list
    """
    return sum(lst) / len(lst)


def return_utc(timezone: str, timestamp: str):
    """Provide datetime object in UTC and local time.

    Args:
        timezone (str): Timezone in a string
        timestamp (str): timestamp in a string

    Returns:
        datetime, datetime: Local time in datetime and UTC datetime
    """
    tz_format = get_timezone(timezone)
    dst = is_dst(timezone, convert_dt_obj(timestamp))
    timestamp_utc_dt = local_datetime(convert_dt_obj(timestamp), tz_format,
                                      dst)
    return dt_to_utc(timestamp_utc_dt), timestamp_utc_dt


def gen_event(parsed_scan: dict):
    """Take a dictionary of scan info and create a calendar event for it.

    Args:
        parsed_scan (dict): parsed scan dictionary

    Returns:
        datetime: datetime object
    """
    # intialize a new event
    e = Event()

    # Set the event name
    e.summary = parsed_scan['name']

    # Set the uuid

    e.uid = parsed_scan['uuid'] + "@schedule.invalid"

    # Set the start time
    e.begin = parser.parse(parsed_scan['starttime_utc'])

    if parsed_scan['endtime_utc']:
        e.end = parser.parse(parsed_scan['endtime_utc'])

    if parsed_scan['scan_type'] == "Agent":
        scan_length_desc = "The agent scan window has been set in the "\
            "scan job."
    elif parsed_scan['scan_type'] == "Network" \
            and parsed_scan['estimated_run'] is True:
        scan_length_desc = "The scan time has been estimated based on the "\
            "average of the previously run jobs."
    elif parsed_scan['scan_type'] == "Network" \
            and parsed_scan['estimated_run'] is False \
            and parsed_scan['endtime_utc']:
        scan_length_desc = "The max scan time has been set in the job."
    else:
        scan_length_desc = "The duration of the calendar event for this job "\
            "has defaulted to 1 hour, as we cannot yet estimate how long it "\
            "will take and no max has been set."

    try:
        parsed_scan['description']
        if not parsed_scan['description']:
            parsed_scan['description'] = "Not Available"
    except KeyError:
        parsed_scan['description'] = "Not Available"

    e.description = "Scan Owner: " + parsed_scan['owner'] + "\n" \
        + "Scan Description: " + parsed_scan['description'] + "\n" \
        + "Scan Type: " + parsed_scan['scan_type'] + "\n" \
        + parsed_scan['scan_targets'] + "\n" + "Scan Length: " \
        + scan_length_desc

    # Set the schedule, if it exists
    if "FREQ=ONETIME" not in parsed_scan['repeatRule'] \
            and parsed_scan['repeatRule'] != "":
        rrule_content = ContentLine(name='RRULE', params={},
                                    value=parsed_scan['repeatRule'])
        e.extra.append(rrule_content)

    dtstamp_set = convert_unix_time(parsed_scan['createdTime'])
    dtstamp_content = ContentLine(name='DTSTAMP', params={}, value=dtstamp_set)
    e.extra.append(dtstamp_content)
    status_content = ContentLine(name='STATUS', params={}, value='CONFIRMED')
    e.extra.append(status_content)

    return (e)


def del_event(event: Event):
    """Mark event as canceled in Calendar Event object.

    Args:
        event (Event): iCalendar Event object

    Returns:
        Event: iCalendar Event object
    """
    e = Event()
    e.uid = event['uuid']
    e.begin = datetime.utcnow()
    cancel_content = ContentLine(name='METHOD', value='CANCEL')
    e.extra.append(cancel_content)
    cancel_content = ContentLine(name='STATUS', value='CANCELLED')
    e.extra.append(cancel_content)
    return (e)
