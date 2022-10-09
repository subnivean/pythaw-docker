import os
from requests.exceptions import ConnectionError
import sys
import time

import awsecrets

# Need to run this *before* importing AmbientAPI
os.environ.update(**awsecrets.env)

from ambient_api.ambientapi import AmbientAPI

class WeatherData():

    def __init__(self, stationnum=0):
        self.stationnum = int(stationnum)
        self.get_latest_data()

    def get_latest_data(self):
        api = AmbientAPI()

        n = 0
        while n < 5:
            try:
                ws = api.get_devices()[self.stationnum]
                break
            except (IndexError, ConnectionError):
                pass

            # Sleep a little and try again
            time.sleep(5)
            n += 1
            # print("Trying again")
        else:
            print("System unreachable.")
            sys.exit()

        self.last_data = ws.last_data

    def get_reading(self, propname):
        return self.last_data[propname]


if __name__ == "__main__":
    wd = WeatherData()
    print(f"{wd.get_reading('temp2f')=}")
    print(f"{wd.get_reading('batt2')=}")
    print(f"{wd.get_reading('date')=}")
