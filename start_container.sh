#!/bin/bash
export PYTHONUNBUFFERED=1
RUNDATE=$(/bin/date "+%Y-%m-%d_%T")

bash_logging() {
    /bin/echo `date +'%F %T '` "INFO" "scan_calendar start_container.sh:" "$@"
}

py_logging() {
    while read -r data; do
       /bin/echo "$data" >> output/logs/$RUNDATE
    done
}

bash_logging "TENB Scan Calendar container started" >> output/logs/$RUNDATE
/usr/local/bin/python -u scan_calendar.py 2>&1 | tee -a output/logs/$RUNDATE
bash_logging "TENB Scan Calendar container finished" >> output/logs/$RUNDATE