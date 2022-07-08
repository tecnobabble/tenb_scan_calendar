import json
from tenable.sc import TenableSC
from ics import Event, Calendar, ContentLine
import ast
import lib.tenb_common
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
        parsed_scan = {}
        if scan['schedule']['enabled'] == "true"  and scan['schedule']['start'] != "":
            parsed_scan['raw_timezone'] = scan['schedule']['start'].split('=')[1].split(':')[0]
            parsed_scan['raw_start'] = scan['schedule']['start'].split('=')[1].split(':')[1]
            parsed_scan['starttime_utc'],parsed_scan['starttime_utc_dt'] = lib.tenb_common.return_utc(parsed_scan['raw_timezone'], parsed_scan['raw_start'])

            # We're going to have to do fun things to determine scan endtimes.
            if scan['maxScanTime'] != 'unlimited':
                # 'maxScanTime is in hours, so we convert to seconds
                endtime = (int(scan['maxScanTime']) * 60 * 60)
                parsed_scan['endtime_utc'] = lib.tenb_common.convert_unix_time(int(parsed_scan['starttime_utc_dt'].timestamp()) + endtime)
                parsed_scan['estimated_run'] = False
                parsed_scan['scan_type'] = "Network"
            else:
                parsed_scan['endtime_utc'] = None
                parsed_scan['estimated_run'] = False
                parsed_scan['scan_type'] = "Network"

                #time to do crazy things to determine average scan time
                matching_results = []
                scantime = int()
                # loop through scan results and match up with scan name and policy name
                for result in tsc_scan_results:
                    if scan['name'] == result['name'] and result['details'] == scan['policy']['name'] and result['scanDuration'] != "-1":
                        matching_results.append({'finishTime': result['finishTime'], 'scanDuration': result['scanDuration']})
                matching_results = sorted(matching_results, key=lambda d: d['finishTime'])[-3:]
                if len(matching_results) == 3:
                    for result_match in matching_results:
                        scantime += int(result_match['scanDuration'])
                    endtime = ( scantime / 3 ) 
                    parsed_scan['endtime_utc'] = lib.tenb_common.convert_unix_time(int(parsed_scan['starttime_utc_dt'].timestamp()) + endtime)
                    parsed_scan['estimated_run'] = True
                else:
                    # Set end time at an hour.
                    parsed_scan['endtime_utc'] = lib.tenb_common.convert_unix_time(int(parsed_scan['starttime_utc_dt'].timestamp()) + 3600)
                    parsed_scan['estimated_run'] = ""


            # Display some meaningful data around the scan targets
            asset_list = ""
            asset_targets = ast.literal_eval('{assets}'.format(**scan))
            if len(asset_targets) > 0:
                for x in asset_targets:
                    asset_list+= x['name'] + " "
            parsed_scan['scan_targets'] = "Targeted Assets: " + asset_list + "\n" + \
                "Targeted IPs: " + '{ipList}'.format(**scan)

            # Direct data pulls:
            parsed_scan['name'] = '{name}'.format(**scan)
            parsed_scan['repeatRule'] = '{schedule[repeatRule]}'.format(**scan)
            parsed_scan['createdTime'] = int('{createdTime}'.format(**scan))
            parsed_scan['owner'] = '{owner[username]}'.format(**scan)
            parsed_scan['description'] = '{description}'.format(**scan)
            parsed_scan['uuid'] = '{uuid}'.format(**scan)
        
            # Generate the event
            e = lib.tenb_common.gen_event(parsed_scan)

            # add all to events
            c.events.append(e)
    

    # Let's pull regular agent jobs
    for scan in sc_response_parse(sc.get('agentScan?fields=id,name,description,createdTime,owner,schedule,scanWindow,nessusManager,repository'))['manageable']:
        parsed_scan = {}
        group_list = ""
        agent_group = ""
        parsed_scan['scan_type'] = "Agent"

        if '{schedule[start]}'.format(**scan) != "":
            parsed_scan['raw_timezone'] = '{schedule[start]}'.format(**scan).split('=')[1].split(':')[0]
            parsed_scan['raw_start'] = '{schedule[start]}'.format(**scan).split('=')[1].split(':')[1]
            parsed_scan['starttime_utc'],parsed_scan['starttime_utc_dt'] = lib.tenb_common.return_utc(parsed_scan['raw_timezone'], parsed_scan['raw_start'])
            
            # 'scanWindow should always be defined
            # 'scanWindow' is in minutes, so we convert to seconds
            endtime = (int('{scanWindow}'.format(**scan)) * 60)
            parsed_scan['endtime_utc'] = lib.tenb_common.convert_unix_time(int(parsed_scan['starttime_utc_dt'].timestamp()) + endtime)
            parsed_scan['estimated_run'] = False

            # We have to ask for more data around each agent scan because the tenable.sc api won't let us get it.
            agent_group = sc_response_parse(sc.get('agentScan/' + '{id}'.format(**scan) + '?fields=agentGroups'))['agentGroups']

            if len(agent_group) > 0:
                for x in agent_group:
                    group_list+= x['name'] + " "
            parsed_scan['scan_targets'] = "Targeted Agent Groups: " + group_list

            # direct agent scans don't have UUIDs for some reason, so we have to generate a consistent one based on some info
            as_seed = '{id}'.format(**scan) + '{createdTime}'.format(**scan)
            rd.seed(as_seed)
            parsed_scan['uuid'] = str(uuid.UUID(int=rd.getrandbits(128), version=4))

            # Direct data pulls:
            parsed_scan['name'] = '{name}'.format(**scan)
            parsed_scan['repeatRule'] = '{schedule[repeatRule]}'.format(**scan)
            parsed_scan['createdTime'] = int('{createdTime}'.format(**scan))
            parsed_scan['owner'] = '{owner[username]}'.format(**scan)
            parsed_scan['description'] = '{description}'.format(**scan)

            # Generate the event
            e = lib.tenb_common.gen_event(parsed_scan)
            
            # add all to events
            c.events.append(e)
    
    # Put all the events into the 'calendar'
    return c.events
