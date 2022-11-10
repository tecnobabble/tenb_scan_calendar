# tenb_scan_calendar

Creates an .ics file that can be imported into your calendar management tool of choice to show when scans run and how long they're expected to take.

If a max_scan time or enough scans have previously run (3), the script will define/estimate future scan lengths.  If not available, defaults to 1 hour.

***This tool is not an officially supported Tenable project***

***Use of this tool is subject to the terms and conditions identified below, and is not subject to any license agreement you may have with Tenable***

### Config
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
### Requirements
#### T.sc
* Must be T.sc 5.19 or above
* Must enable API auth application wide
* Must create or use existing API keys for a user that can "Create Scans" as part of their role (Vulnerability Analyst, Security Analyst, Security Manager or custom) and that can manage all objects for all groups.
* Works for direct agent scans and network based scans
* Must be run once per tenable.sc 'organization' (and rename the ics file after each run)

#### T.io
* Get API keys for a user that can manage/see all scans

![example google calendar output](https://res.cloudinary.com/salted-security/image/upload/v1668117471/Github/tenb_google_calendar_visual.png)

#### Nessus
* Get API keys for a user that can manage/see all scans

Tested on python 3.10; will likely work on 3.6+

### Todo:
* ~~Support Direct Agent Scans~~
* ~~Pull network scan completetion times to estimate future runtime~~
* ~~maintain state to support deleted events~~
* Support multiple orgs
* ~~Support t.io~~
* ~~Support Nessus (all flavors)~~  
* Support T.sc Director

### Thanks
Made possible largely by ics-py (https://github.com/ics-py/ics-py)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[GNU GPL](https://choosealicense.com/licenses/gpl-3.0/)
