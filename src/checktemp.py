#!/usr/bin/env python3
import glob
import time
import datetime
import numpy as np

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

AVGINTERVAL = 15  # Interval for averaging of readings
MEANOUTFILE = "/data/meantemps.out"

sp = SmartPlug(SPIP)

meanoutfh = open(MEANOUTFILE, "ab", 0)

cnt = 0
temps = []
msgqueue = []
lastmeantemp = None
tdir = u"\u2198"
minsincelastchg = 0
last30 = []  # Container to hold last 30 minutes
while True:
    cnt += 1

    tempF = float(aw.get_reading(SENSORNAME))
    temps.append(tempF)

    curtime = datetime.datetime.now().isoformat().split('.')[0]

    if cnt % AVGINTERVAL != 0:
        # print(f"secs={AVGINTERVAL - cnt % AVGINTERVAL:2d} cnt={cnt} "
        #       f"temp={tempF:.2f} switch:{sp.is_on}")
        pass
    else:
        #print("Here!")

        meantemp = np.median(temps)

        last30.append(meantemp)
        if len(last30) > 30:
            last30.pop(0)

        rmean10ndx = min(len(last30), 10)
        rmean10 = np.mean(last30[-rmean10ndx:])

        if lastmeantemp is not None:
            if meantemp - lastmeantemp > 0:
                tdir = u"\u2197"
                minsincelastchg = 0
            elif meantemp - lastmeantemp < 0:
                tdir = u"\u2198"
                minsincelastchg = 0

        lastmeantemp = meantemp

        dline = bytes(f"{curtime} {meantemp:.2f} {tdir} ({minsincelastchg}) {rmean10:.2f}\n", "UTF-8")
        meanoutfh.write(dline)

        minsincelastchg += 1

        temps = []  # Reset

        if meantemp < ALERTTEMP:
            if sp.is_on:
                msgqueue.append(("*** Heater problem? ***",
                                 f"Temp dropped below {ALERTTEMP}!", False))
                sp.on()  # Try again
            pass
        elif meantemp < MINTEMP:
            if sp.is_off:
                msgqueue.append(("Turning on the heater",
                                 f"Temp dropped below {MINTEMP}", False))
                sp.on()
            pass
        elif meantemp > MAXTEMP:
            if sp.is_on:
                msgqueue.append(("Turning off the heater",
                                 f"Temp above {MAXTEMP}", False))
                sp.off()
            pass

        # Send any queued messages
        while len(msgqueue) > 0:
            subj, msg, alert = msgqueue.pop(0)
            try:
                mailsend.send(subj, msg, alert=alert)
                #print("Mail sent!")
            except:
                #print("Mail not sent!")
                pass

    # Set delay to get ~1 second between readings
    time.sleep((60 / AVGINTERVAL) - 1 + 0.121)
