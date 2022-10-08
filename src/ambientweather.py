import os
from requests.exceptions import ConnectionError
import sys
import time

import awsecrets

# Need to run this *before* importing AmbientAPI
os.environ.update(**awsecrets.env)

from ambient_api.ambientapi import AmbientAPI

def get_reading(sensorname):
    api = AmbientAPI()

    n = 0
    while n < 5:
        try:
            ws = api.get_devices()[0]
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

    return ws.last_data[sensorname]


if __name__ == "__main__":
    sensorname = 'temp2f'
    print(f"{get_reading(sensorname)=}")
