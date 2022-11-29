FROM python:3-slim-buster

RUN apt-get update && apt-get install -y git && apt-get -y upgrade
RUN /usr/local/bin/python -m pip install --upgrade pip

RUN useradd -ms /bin/bash scan_calendar
COPY --chown=scan_calendar:scan_calendar requirements.txt /home/scan_calendar/

RUN pip3 install -r /home/scan_calendar/requirements.txt

COPY --chown=scan_calendar:scan_calendar scan_calendar.py start_container.sh /home/scan_calendar/
COPY --chown=scan_calendar:scan_calendar lib /home/scan_calendar/lib
RUN chmod +x /home/scan_calendar/scan_calendar.py /home/scan_calendar/start_container.sh
USER scan_calendar

RUN mkdir -p /home/scan_calendar/output/logs

ENV IS_TENB_SCAN_CALENDAR_DOCKER=True

ENTRYPOINT [ "/bin/bash", "start_container.sh" ]

WORKDIR /home/scan_calendar

HEALTHCHECK NONE