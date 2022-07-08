import json
from tenable.nessus import Nessus
from ics import Event, Calendar, ContentLine
from pprint import pprint
import lib.tenb_common
import ast

def nessus_parse(nessus, c):
    for scan in nessus.scans.list()['scans']:
        parsed_scan = {}
        # Scan must be enabled and not have triggers in order to have a calendar schedule
        if scan['enabled'] == True and scan['starttime']:# and scan['name'] == "Full plugin test":
            scan_details = nessus.editor.details('scan', scan['id'])

            # Figure out start timing
            parsed_scan['raw_timezone'] = scan['timezone']
            parsed_scan['raw_start'] = scan['starttime']
            parsed_scan['starttime_utc'],parsed_scan['starttime_utc_dt'] = lib.tenb_common.return_utc(parsed_scan['raw_timezone'], parsed_scan['raw_start'])

            # End time's are fun
            if scan['type'] == "remote" or scan['type'] == "local" and scan['status'] == "completed" or scan['status'] == "aborted" or scan['status'] == "running":
                scan_time = 0
                history_count = 0
                avg_scan_time = 0
                scan_history = nessus.scans.details(scan['id'])['history']
                for item in scan_history:
                    if item['status'] == "completed":
                        scan_time += item['last_modification_date'] - item['creation_date']
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
                    if scan_item['id'] == "description":
                        parsed_scan['description'] = scan_item["default"]

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

                scan_ag_list = ""
                for item in scan_details['settings']['basic']['inputs']:
                    if scan_item['id'] == "description":
                        parsed_scan['description'] = scan_item["default"]

                    if item['id'] == "scan_time_window":
                        scan_window = int(item['default']) * 60
                        parsed_scan['estimated_run'] = False
                        parsed_scan['scan_type'] = "Agent"
                        parsed_scan['endtime_utc'] = lib.tenb_common.convert_unix_time(int(parsed_scan['starttime_utc_dt'].timestamp()) + scan_window)

                    # Get a list of agent groups in the scan
                    if item['id'] == "agent_group_id":
                        for agent_group in item['default']:
                            for ag_group in item['options']:
                                if agent_group == ag_group['id']:
                                    scan_ag_list+=  ag_group['name'] + " "
                parsed_scan['scan_targets'] = "Targeted Agent Groups: " + scan_ag_list

            # Direct data pulls:
            parsed_scan['name'] = scan['name']
            parsed_scan['repeatRule'] = scan['rrules'] 
            parsed_scan['createdTime'] = int(scan['creation_date'])
            parsed_scan['owner'] = scan['owner']
            parsed_scan['uuid'] = scan['uuid'][9:]

            # Generate the event
            e = lib.tenb_common.gen_event(parsed_scan)

            # add all to events
            c.events.append(e)

    return c.events

