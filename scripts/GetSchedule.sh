#!/bin/sh
/usr/local/bin/python3 /root/scripts/01_get_schedule_AG.py
/usr/local/bin/python3 /root/scripts/02_match_keyword.py
chmod 755 -R /root/scripts/scripts
chmod 755 -R /root/scripts/json
#/usr/local/bin/python3 /root/scripts/03_reservation.py
