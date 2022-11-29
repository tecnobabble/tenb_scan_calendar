# tenb_scan_calendar

Creates an .ics file that can be imported into your calendar management tool of choice to show when Tenable Nessus Network scans or agent assessments run and how long they're expected to take.  Supports Tenable.sc, Tenable.io VM, and Nessus (all flavors).

***This tool is not an officially supported Tenable project***

***Use of this tool is subject to the terms and conditions identified below, and is not subject to any license agreement you may have with Tenable***

### General usage
Docker is recommended; be sure to pass the proper .env file
```
docker run -d --rm --env-file .env -v ${PWD}/:/home/scan_calendar/output/ -v ${PWD}/logs:/home/scan_calendar/output/logs tenb_scan_calendar:latest
```

You can also just run from Python directly:
```
python scan_calendar.py
```

The output will be a file called `tenable_scans.ics` produced.  Load this file into [Google](https://support.google.com/calendar/answer/37118)/[Outlook Calendar](https://support.microsoft.com/en-us/office/import-calendars-into-outlook-8e8364e1-400e-4c0f-a573-fe76b5a2d379).  

![example google calendar output](https://res.cloudinary.com/salted-security/image/upload/v1668117471/Github/tenb_google_calendar_visual.png)

You could also run this container/script on a schedule and copy the file to a webserver; subscribe to the produced calendar file [Google](https://support.google.com/calendar/answer/37100)/[Outlook](https://support.microsoft.com/en-us/office/import-or-subscribe-to-a-calendar-in-outlook-com-cff1429c-5af6-41ec-a5b4-74f2c278e98c) and it will auto update when changes are made to the relevant scan jobs.

### Requirements
#### T.sc
* Must be T.sc 5.19 or above
* Must enable API auth application wide
* Must create or use existing API keys for a user that can "Create Scans" as part of their role (Vulnerability Analyst, Security Analyst, Security Manager or custom) and that can manage all objects for all groups.
* Works for direct agent scans and network based scans
* Must be run once per tenable.sc 'organization' (and rename the ics file after each run)

#### T.io
* Get API keys for a user that can manage/see all scans

#### Nessus
* Get API keys for a user that can manage/see all scans

Tested on python 3.10+; will likely work on 3.6+

### Configuration
Sample .env file in same folder as script:

```
SC_ACCESS_KEY=aaaaaaabbbbbbccccddddeeeffff1234  
SC_SECRET_KEY=aaaaaaabbbbbbccccddddeeeffff1234   
SC_ADDRESS=10.0.0.100  
SC_PORT=443  

IO_URL=https://cloud.tenable.com
IO_ACCESS_KEY=aaaaaaabbbbbbccccddddeeeffff1234
IO_SECRET_KEY=aaaaaaabbbbbbccccddddeeeffff1234

NESSUS_URL=https://10.0.0.101:8834
NESSUS_ACCESS_KEY=aaaaaaabbbbbbccccddddeeeffff1234
NESSUS_SECRET_KEY=aaaaaaabbbbbbccccddddeeeffff1234
```

### Notes
* If a max_scan time or enough scans have previously run (3), the script will define/estimate future scan lengths.  If not available, defaults to 1 hour.
* To subscribe to a calendar, the .ics file has to be public if using a cloud email service like Google/Outlook.com.  It has to be reachable from your internal calendar software install otherwise (ex: Outlook installed locally on your computer).

### Troubleshooting
Add "DEBUG=TRUE" to your env file and re-run the script. See the logs in the generated 'logs' folder. If you're still unsure, open an Issue.

### Todo:
* ~~Support Direct Agent Scans~~
* ~~Pull network scan completetion times to estimate future runtime~~
* ~~maintain state to support deleted events~~
* Support multiple orgs
* ~~Support t.io~~
* ~~Support Nessus (all flavors)~~  
* Support T.sc Director
* ~~support running from docker~~
* ~~support debug mode~~

### Thanks
Made possible largely by ics-py (https://github.com/ics-py/ics-py)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[GNU GPL](https://choosealicense.com/licenses/gpl-3.0/)
