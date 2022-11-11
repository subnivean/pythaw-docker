Crawl Space Pump House Monitoring and Control
---------------------------------------------
Running on an RPi4 with 64-bit Raspberry Pi OS

Clone into `/home/pi/pythaw-docker`.

Note that after cloning, you *must* copy `src/gsecrets_example.py`
to `src/gsecrets.py` and modify with actual data.

Invoked from crontab as follows:

```
* * * * * /home/pi/pythaw-docker/run_app.sh
```

Docker Instructions
-------------------------
Build via `docker build . -t pythaw`.

Run via `./run_docker.sh`.

Access internal bash shell via `./run_bash.sh`.
