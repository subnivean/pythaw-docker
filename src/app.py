#!/usr/bin/env python3
import datetime
import subprocess
import sys

# Current directory
import mailsend
from smartplug import SmartPlug

# All temps in degrees F
MINTEMP = 36.0
MAXTEMP = 39.0
ALERTTEMP = 35.5
SPIP = 23  # SmartPlug IP address (in 192.168.1.xx range)

# Weather station and sensor settings
WXSTATIONNUM = 0  # Old station, per Ambientweather
WXSENSORNUM = 2
WXTEMPSENSOR = f"temp{WXSENSORNUM}f"
WXBATTNAME = f"batt{WXSENSORNUM}"
WXTABLENAME = f"dbtable{WXSTATIONNUM}"

# Data to access the Ambientweather sqlite database
AWIP = '192.168.1.10'
AWDBPATH = "/home/pi/ambientweather-docker/data/ambientweather.sqlite"
REMOTEUSER = "pi"
LOCALKEYPATH = "/app/id_rsa_rpi"
AWQUERY = f"""\
    'SELECT date,{WXTEMPSENSOR},{WXBATTNAME}
     FROM {WXTABLENAME}
     ORDER BY ROWID DESC
     LIMIT 1;'"""

LASTRUNFILE = "/data/lastrun"

curtime = datetime.datetime.now()

try:
    sp = SmartPlug(SPIP)
except:
    if curtime.minute == 0:
        mailsend.send(f"SmartPlug #{SPIP} is not responding", "Sorry!")
    sys.exit()

try:
    res = subprocess.run([
        'ssh', '-q', '-o'
        'StrictHostKeyChecking=no',
        '-i', LOCALKEYPATH,
        '-l', REMOTEUSER,
        AWIP,
            "sqlite3", AWDBPATH, AWQUERY
    ], capture_output=True, encoding='utf-8')
except:
    if curtime.minute == 0:
        mailsend.send(f"Problem accessing Ambientweather", f"{WXSTATIONNUM=}")
    sys.exit()

# Parse the data from the last database record
lastreport, tempF, battlevel = res.stdout.strip().split('|')

try:
    tempF = float(tempF)
except ValueError:
    # Send 'sensor offline' message every hour
    if curtime.minute == 0:
        mailsend.send(f"Sensor #{WXSENSORNUM} is offline",
                      f"No data via Ambientweather, sorry.")
    sys.exit(1)

try:
    battlevel = float(battlevel)
except ValueError:
    # Send 'sensor offline' message every hour
    if curtime.minute == 0:
        mailsend.send(f"Sensor #{WXSENSORNUM} is offline",
                      f"No data via Ambientweather, sorry.")
    sys.exit(1)

# Send 'low battery' message once a day
if battlevel < 1.0 and curtime.hour == 12 and curtime.minute == 0:
    mailsend.send(f"Low battery level on sensor #{WXSENSORNUM}",
                  f"Current level: {battlevel}")

# Send 'not reporting' message every hour
lastreportdt = datetime.datetime.fromisoformat(lastreport.split('+')[0])
timedeltasec = (curtime - lastreportdt).seconds
if timedeltasec > 3600 and curtime.minute == 0:
    mailsend.send(f"Sensor #{WXSENSORNUM} not reporting",
                  f"Last report: {lastreport}")

#print(f"{battlevel=}")
#print(f"{lastreport=}")
#print(f"{lastreportdt=}")
#print(f"{curtime.hour=}")
#print(f"{timedeltasec=}")

lastrunfh = open(LASTRUNFILE, "w")

curtimeiso = curtime.isoformat().split('.')[0]
dline = f"{curtimeiso} {tempF:.2f}\n"
lastrunfh.write(dline)

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

