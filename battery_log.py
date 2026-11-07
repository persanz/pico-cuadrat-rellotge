# Periodic raw observations; charge status is not a USB-presence sensor.
import os
import time

_PATH = "battery_usage.csv"
_INTERVAL = 300000
_MAX_BYTES = 262144
_started = time.ticks_ms()
_last = None

def update(adc, charging):
    global _last
    now = time.ticks_ms()
    if _last is not None and time.ticks_diff(now, _last) < _INTERVAL:
        return
    _last = now
    try:
        try:
            size = os.stat(_PATH)[6]
        except OSError:
            size = 0
        if size >= _MAX_BYTES:
            return
        raw = sum(adc.read_u16() for _ in range(16)) // 16
        elapsed = time.ticks_diff(now, _started) // 1000
        with open(_PATH, "a") as f:
            if not size:
                f.write("local_time,elapsed_s,adc_raw,voltage_v,charging_status\n")
            t = time.localtime()
            f.write("%04d-%02d-%02dT%02d:%02d:%02d,%d,%d,%.3f,%d\n" %
                    (t[0],t[1],t[2],t[3],t[4],t[5],elapsed,raw,
                     raw * 9.9 / 65535, 1 if charging else 0))
    except OSError:
        pass
