import json
from tenable.sc import TenableSC
from ics import Event, Calendar, ContentLine
import ast
import lib.common
import uuid
import random

# Define Functions
def sc_response_parse(response):
    return json.loads(response.text)['response']

def sc_parse(sc, c):
    rd = random.Random()

    # Pull scan results as we will use them later
    tsc_scan_results = sc_response_parse(sc.get('scanResult?fields=id,name,finishTime,description,repository,details,scanDuration&filter=optimizeCompletedScans'))['manageable']

    # All the actual processing goes here for network scans
    for scan in sc.scans.list(['id','name','policy','schedule', 'createdTime', 'owner','maxScanTime', 'ipList', 'assets', 'description'])['manageable']:
        if '{schedule[enabled]}'.format(**scan) == "true"  and '{schedule[start]}'.format(**scan) != "":
            raw_timezone = '{schedule[start]}'.format(**scan).split('=')[1].split(':')[0]
            raw_start = '{schedule[start]}'.format(**scan).split('=')[1].split(':')[1]
            starttime_utc,starttime_utc_dt = lib.common.return_utc(raw_timezone, raw_start)

            # We're going to have to do fun things to determine scan endtimes.
            if '{maxScanTime}'.format(**scan) != 'unlimited':
                # 'maxScanTime is in hours, so we convert to seconds
                endtime = (int('{maxScanTime}'.format(**scan)) * 60 * 60)
                endtime_utc = lib.common.convert_unix_time(int(starttime_utc_dt.timestamp()) + endtime)
                estimated_run = False
                scan_type = "Network"
            else:
                endtime_utc = None
                estimated_run = False
                scan_type = "Network"

                #time to do crazy things to determine average scan time
                matching_results = []
                scantime = int()
                # loop through scan results and match up with scan name and policy name
                for result in tsc_scan_results:
                    if '{name}'.format(**scan) == '{name}'.format(**result) and '{details}'.format(**result) == '{policy[name]}'.format(**scan) and '{scanDuration}'.format(**result) != "-1":
                        matching_results.append({'finishTime': '{finishTime}'.format(**result), 'scanDuration': '{scanDuration}'.format(**result)})
                matching_results = sorted(matching_results, key=lambda d: d['finishTime'])[-3:]
                if len(matching_results) == 3:
                    for result_match in matching_results:
                        scantime += int(result_match['scanDuration'])
                    endtime = ( scantime / 3 ) 
                    endtime_utc = lib.common.convert_unix_time(int(starttime_utc_dt.timestamp()) + endtime)
                    estimated_run = True

            # Display some meaningful data around the scan targets
            asset_list = ""
            asset_targets = ast.literal_eval('{assets}'.format(**scan))
            if len(asset_targets) > 0:
                for x in asset_targets:
                    asset_list+= x['name'] + " "
            scan_targets = "Targeted Assets: " + asset_list + "\n" + \
                "Targeted IPs: " + '{ipList}'.format(**scan)

            # Generate the event
            e = lib.common.gen_event(
                    '{name}'.format(**scan), \
                    '{schedule[repeatRule]}'.format(**scan), \
                    raw_start, \
                    raw_timezone, \
                    int('{createdTime}'.format(**scan)), \
                    '{owner[username]}'.format(**scan), \
                    scan_type, \
                    '{description}'.format(**scan), \
                    '{uuid}'.format(**scan), \
                    scan_targets, \
                    starttime_utc, \
                    endtime_utc, \
                    estimated_run
                    )
            # add all to events
            c.events.append(e)
    

    # Let's pull regular agent jobs
    for scan in sc_response_parse(sc.get('agentScan?fields=id,name,description,createdTime,owner,schedule,scanWindow,nessusManager,repository'))['manageable']:
        group_list = ""
        agent_group = ""
        scan_type = "Agent"

        if '{schedule[start]}'.format(**scan) != "":
            raw_timezone = '{schedule[start]}'.format(**scan).split('=')[1].split(':')[0]
            raw_start = '{schedule[start]}'.format(**scan).split('=')[1].split(':')[1]
            starttime_utc,starttime_utc_dt = lib.common.return_utc(raw_timezone, raw_start)
            
            # 'scanWindow should always be defined
            # 'scanWindow' is in minutes, so we convert to seconds
            endtime = (int('{scanWindow}'.format(**scan)) * 60)
            endtime_utc = lib.common.convert_unix_time(int(starttime_utc_dt.timestamp()) + endtime)
            estimated_run = False

            # We have to ask for more data around each agent scan because the tenable.sc api won't let us get it.
            agent_group = sc_response_parse(sc.get('agentScan/' + '{id}'.format(**scan) + '?fields=agentGroups'))['agentGroups']

            if len(agent_group) > 0:
                for x in agent_group:
                    group_list+= x['name'] + " "
            scan_targets = "Targeted Agent Groups: " + group_list

            # direct agent scans don't have UUIDs for some reason, so we have to generate a consistent one based on some info
            as_seed = '{id}'.format(**scan) + '{createdTime}'.format(**scan)
            rd.seed(as_seed)
            as_uuid = str(uuid.UUID(int=rd.getrandbits(128), version=4))

            # Generate the event
            e = lib.common.gen_event(
                    '{name}'.format(**scan), \
                    '{schedule[repeatRule]}'.format(**scan), \
                    raw_start, \
                    raw_timezone, \
                    int('{createdTime}'.format(**scan)), \
                    '{owner[username]}'.format(**scan), \
                    scan_type, \
                    '{description}'.format(**scan), \
                    as_uuid, \
                    scan_targets, \
                    starttime_utc, \
                    endtime_utc, \
                    estimated_run
                    )
            
            # add all to events
            c.events.append(e)
    
    # Put all the events into the 'calendar'
    return c.events
