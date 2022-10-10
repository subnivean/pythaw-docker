#!/usr/bin/env python3
import datetime
import sys

# Current directory
from ambientweather import WeatherData
import mailsend
from smartplug import SmartPlug

# All temps in degrees F
MINTEMP = 36.0
MAXTEMP = 39.0
ALERTTEMP = 35.5

WXSTATIONNUM = 0  # Per Ambientweather
WXSENSORNUM = 2
WXTEMPSENSOR = f"temp{WXSENSORNUM}f"
WXBATTNAME = f"batt{WXSENSORNUM}"

SPIP = 23  # SmartPlug IP address (in 192.168.1.xx range)

MEANOUTFILE = "/data/meantemps.out"

curtime = datetime.datetime.now()

try:
    sp = SmartPlug(SPIP)
except:
    if curtime.minute == 0:
        mailsend.send(f"SmartPlug #{SPIP} is not responding", "Sorry!")
    sys.exit()

try:
    aw = WeatherData(WXSTATIONNUM)
except:
    if curtime.minute == 0:
        mailsend.send(f"Problem accessing Ambientweather", f"{WXSTATIONNUM=}")
    sys.exit()

lastreport = aw.get_reading('date')
lastreportdt = datetime.datetime.fromisoformat(lastreport.split('.')[0])
timedeltasec = (curtime - lastreportdt).seconds

try:
    battlevel = float(aw.get_reading(WXBATTNAME))
except KeyError:
    # Send 'sensor offline' message every hour
    if curtime.minute == 0:
        mailsend.send(f"Sensor #{WXSENSORNUM} is offline",
                      f"No data via Ambientweather, sorry.")
    sys.exit()

# Send 'low battery' message once a day
if battlevel < 1.0 and curtime.hour == 12 and curtime.minute == 0:
    mailsend.send(f"Low battery level on sensor #{WXSENSORNUM}",
                  f"Current level: {battlevel}")

# Send 'not reporting' message every hour
if timedeltasec > 3600 and curtime.minute == 0:
    mailsend.send(f"Sensor #{WXSENSORNUM} not reporting",
                  f"Last report: {lastreport}")

#print(f"{battlevel=}")
#print(f"{lastreport=}")
#print(f"{lastreportdt=}")
#print(f"{curtime.hour=}")
#print(f"{timedeltasec=}")

meanoutfh = open(MEANOUTFILE, "ab", 0)

tempF = float(aw.get_reading(WXTEMPSENSOR))

curtimeiso = curtime.isoformat().split('.')[0]
dline = bytes(f"{curtimeiso} {tempF:.2f}\n", "UTF-8")
meanoutfh.write(dline)

if tempF < ALERTTEMP:
    if sp.is_on:
        try:
            mailsend.send("*** Heater problem? ***",
                          f"Temp dropped below {ALERTTEMP}!")
        except:
            pass
    sp.on()
elif tempF < MINTEMP:
    if sp.is_off:
        try:
            mailsend.send("Turning on the heater",
                          f"Temp dropped below {MINTEMP}")
        except:
            pass
    sp.on()
elif tempF > MAXTEMP:
    if sp.is_on:
        try:
            mailsend.send("Turning off the heater",
                          f"Temp above {MAXTEMP}")
        except:
            pass
    sp.off()

