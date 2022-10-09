#!/usr/bin/env python3
import datetime

# Current directory
import ambientweather as aw
import mailsend
from smartplug import SmartPlug

# All temps in degrees F
MINTEMP = 36.0
MAXTEMP = 39.0
ALERTTEMP = 35.5

SENSORNAME = "temp2f"

SPIP = 23  # SmartPlug IP address (in 192.168.1.xx range)

MEANOUTFILE = "/data/meantemps.out"

sp = SmartPlug(SPIP)

meanoutfh = open(MEANOUTFILE, "ab", 0)

curtime = datetime.datetime.now().isoformat().split('.')[0]
tempF = float(aw.get_reading(SENSORNAME))

dline = bytes(f"{curtime} {tempF:.2f}\n", "UTF-8")
meanoutfh.write(dline)

if tempF < ALERTTEMP:
    if sp.is_on:
        mailsend.send("*** Heater problem? ***",
                      f"Temp dropped below {ALERTTEMP}!")
    sp.on()
elif tempF < MINTEMP:
    if sp.is_off:
        mailsend.send("Turning on the heater",
                      f"Temp dropped below {MINTEMP}")
    sp.on()
elif tempF > MAXTEMP:
    if sp.is_on:
        mailsend.send("Turning off the heater",
                      f"Temp above {MAXTEMP}")
    sp.off()

