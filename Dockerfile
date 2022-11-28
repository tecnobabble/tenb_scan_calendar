FROM python:3-slim-buster

RUN apt-get update && apt-get install -y git && apt-get -y upgrade
RUN /usr/local/bin/python -m pip install --upgrade pip

RUN useradd -ms /bin/bash scan_calendar
COPY --chown=scan_calendar:scan_calendar requirements.txt /home/scan_calendar/

RUN pip3 install -r /home/scan_calendar/requirements.txt

COPY --chown=scan_calendar:scan_calendar scan_calendar.py /home/scan_calendar/
COPY --chown=scan_calendar:scan_calendar lib /home/scan_calendar/lib
RUN chmod +x /home/scan_calendar/scan_calendar.py
USER scan_calendar

RUN mkdir /home/scan_calendar/output

ENV IS_TENB_SCAN_CALENDAR_DOCKER=True

ENTRYPOINT ["python", "-u", "scan_calendar.py"]

WORKDIR /home/scan_calendar

HEALTHCHECK NONE