import json
from tenable.io import TenableIO
from ics import Event, Calendar, ContentLine
from pprint import pprint
import lib.tenb_common
import ast

def io_parse(tio, c):
    for scan in tio.scans.list():
        
        parsed_scan = {}
        # Scan must be enabled and not have triggers in order to have a calendar schedule
        if scan['enabled'] == True and scan['has_triggers'] == False and scan['status'] != 'empty':# and scan['name'] == "Full plugin test":
            scan_details = lib.tenb_common.tenb_response_parse(tio.get('editor/scan/' + scan['schedule_uuid']))

            # Figure out start timing
            parsed_scan['raw_timezone'] = '{timezone}'.format(**scan)
            parsed_scan['raw_start'] = '{starttime}'.format(**scan)
            parsed_scan['starttime_utc'],parsed_scan['starttime_utc_dt'] = lib.tenb_common.return_utc(parsed_scan['raw_timezone'], parsed_scan['raw_start'])

            # End time's are fun
            if scan['type'] == "remote" or scan['type'] == "ps" and scan['status'] == "completed" or scan['status'] == "aborted":
                scan_time = 0
                history_count = 0
                avg_scan_time = 0
                scan_history = tio.scans.history(scan['schedule_uuid'], limit=10, sort=(("start_date", "desc"),))
                for item in scan_history:
                    if item['status'] == "completed":
                        scan_time += item['time_end'] - item['time_start']
                        history_count += 1
                        if history_count == 3:
                            avg_scan_time = round(int(scan_time) / 3)
                            break
                if avg_scan_time > 1:
                    parsed_scan['endtime_utc'] = lib.tenb_common.convert_unix_time(int(parsed_scan['starttime_utc_dt'].timestamp()) + avg_scan_time)
                    parsed_scan['estimated_run'] = True
                    parsed_scan['scan_type'] = "Network"
                else:
                    parsed_scan['estimated_run'] = False
                    parsed_scan['scan_type'] = "Network"
                    parsed_scan['endtime_utc'] = lib.tenb_common.convert_unix_time(int(parsed_scan['starttime_utc_dt'].timestamp()) + 3600)
            
                # Display some meaningful data around the scan targets
                tag_list = ""
                tg_list = ""
                ip_list = ""
                for scan_item in scan_details['settings']['basic']['inputs']:
                    if scan_item['id'] == "tag_targets":
                        for tag_item in scan_item['default']:
                            for tag_select in scan_item['options']:
                                if tag_item == tag_select['uuid']:
                                    tag_list+=  tag_select['category_name'] + ":" + tag_select['value'] + ""

                    if scan_item['id'] == "text_targets" and scan_item["default"]:
                        ip_list = scan_item["default"]

                    if scan_item['id'] == "asset_lists":
                        for tg_item in scan_item['default']:
                            for tg_select in scan_item['options']:
                                if tg_item == tg_select['id']:
                                    tg_list+=  tg_select['name'] + " "

                parsed_scan['scan_targets'] = "Targeted Tags: " + tag_list + "\n" + \
                    "Targeted IPs: " + ip_list + "\n" + \
                    "Targeted Target Groups:" + tg_list

            elif scan['type'] == 'agent':
                for item in scan_details['settings']['basic']['groups']:
                    if item['name'] == "agent_scan_launch_type":
                        scan_window = int(item["inputs"][0]['default']) * 60
                parsed_scan['estimated_run'] = False
                parsed_scan['scan_type'] = "Agent"
                parsed_scan['endtime_utc'] = lib.tenb_common.convert_unix_time(int(parsed_scan['starttime_utc_dt'].timestamp()) + scan_window)

                # Get a list of agent groups in the scan
                scan_ag_list = ""
                for item in scan_details['settings']['basic']['inputs']:
                    if item['name'] == "Agent Groups":
                        for agent_group in item['default']:
                            for ag_group in item['options']:
                                if agent_group == ag_group['id']:
                                    scan_ag_list+=  ag_group['name'] + " "
                parsed_scan['scan_targets'] = "Targeted Agent Groups: " + scan_ag_list

            # Direct data pulls:
            parsed_scan['name'] = '{name}'.format(**scan)
            parsed_scan['repeatRule'] = '{rrules}'.format(**scan)
            parsed_scan['owner'] = '{owner}'.format(**scan)
            parsed_scan['uuid'] = '{schedule_uuid}'.format(**scan)[9:]
            parsed_scan['createdTime'] = int('{creation_date}'.format(**scan))

            # Generate the event
            e = lib.tenb_common.gen_event(parsed_scan)

            # add all to events
            c.events.append(e)

    return c.events
