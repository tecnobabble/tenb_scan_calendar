# tenb_scan_calendar

Creates an .ics file that can be imported into your calendar management tool of choice to show when scans run and how long they're expected to take.

t.sc supported initially, t.io support in future release

### Config
Sample .env file in same folder as script:

```
SC_ACCESS_KEY=aaaaaaabbbbbbccccddddeeeffff1234  
SC_SECRET_KEY=aaaaaaabbbbbbccccddddeeeffff1234   
SC_ADDRESS=10.0.0.102  
SC_PORT=443  

IO_URL=https://cloud.tenable.com
IO_ACCESS_KEY=aaaaaaabbbbbbccccddddeeeffff1234
IO_SECRET_KEY=aaaaaaabbbbbbccccddddeeeffff1234
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

Tested on python 3.10; will likely work on 3.6+

### Todo:
* ~~Support Direct Agent Scans~~
* ~~Pull network scan completetion times to estimate future runtime~~
* Support multiple orgs
* ~~Support t.io~~
* Support Nessus (all flavors)  
* Support T.sc Director

### Problematic things:
* Agent Sync Jobs in T.sc 
    * All the details we need are in the Agent Manager, not T.sc

### Thanks
Made possible largely by ics-py (https://github.com/ics-py/ics-py)