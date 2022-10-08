# Works with CloudFree Tasmota-based smart plugs
import requests

URLTMPL = "http://192.168.1.{ip}"
POWERCHK = "/cm?cmnd=Power"
POWERON = "/cm?cmnd=Power%20On"
POWEROFF = "/cm?cmnd=Power%20Off"

class SmartPlug():
    def __init__(self, ip):
        self.ip = str(ip)
        self.url = URLTMPL.format(ip=self.ip)

    def on(self):
        requests.post(self.url + POWERON)

    def off(self):
        requests.post(self.url + POWEROFF)

    @property
    def is_on(self):
        res = requests.post(self.url + POWERCHK)
        return 'ON' in res.content.decode('utf-8')  

    @property
    def is_off(self):
        res = requests.post(self.url + POWERCHK)
        return 'OFF' in res.content.decode('utf-8')  

if __name__ == "__main__":
    import time
    sp = SmartPlug(23)

    print(f"Power status: {sp.is_on}")

    CYCLES = 2
    for n in range(CYCLES):
        print(f"{n + 1} of {CYCLES} cycles...")
        sp.on()
        print(f"Power status: {sp.is_on}")
        time.sleep(1)
        sp.off()
        print(f"Power status: {sp.is_on}")
        time.sleep(1)
        

