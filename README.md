Crawl Space Pump House Monitoring and Control

Running on an RPi4 with 64-bit Raspberry Pi OS

Clone into `/home/pi/pythaw-docker`.

Note that after cloning, you *must* copy `src/gsecrets_example.py`
to `src/gsecrets.py` and modify with actual data.

Invoked from `rc.local` as follows:

```
cd /home/pi/pythaw-docker && ./run_docker.sh &
```

Docker Instructions
-------------------------
NOTE: `sudo` is required below for access to 
      `/dev/mem`, among other things.

Build via `sudo docker build . -t pythaw`
Run via `sudo ./run_docker.sh`
Access internal bash shell via `sudo ./run_bash.sh`
