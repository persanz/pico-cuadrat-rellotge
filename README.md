# pico-cuadrat-rellotge

A tiny **MicroPython clock** for the **Waveshare RP2350-Touch-LCD-1.54** (round 240×240).

```
     23:59:27        ← time      (white)
     02 Nov 2026     ← date      (cyan)
       Monday        ← weekday   (blue)
     Battery 75% ⚡   ← estimated battery level and charging indicator
```

The battery indicator reads GPIO 29 using the Waveshare demo’s voltage scaling. Its
percentage is a rough voltage-based estimate for a single Li-ion cell, not a charge
measurement. Readings below 3.0 V or above 4.3 V show `?` instead of a percentage.
A bolt appears when the charger status indicates charging.

## Why a helper script is needed

This board has **no WiFi and no battery-backed RTC**, so the Pico cannot know the time by
itself. A host (Mac/Linux/Windows) sends the date & time over the **USB serial** link every
few seconds; the Pico stores it in its RTC and ticks the seconds locally in between.

```
host  --"S|DT:YYYY-MM-DD:HH:MM:SS:WD|TS:HH:MM:SS"-->  Pico (USB CDC)
Pico  <--"K" (acknowledgement)------------------------
```

## Works without the host

The app **persists the time to flash** (`clock.dat`), written on every sync *and once a minute*.
At boot it restores the RTC from that file, so after a power cycle the clock resumes from the last
known time instead of showing `syncing…` — no host required.

> Limitation: the RP2350 has no battery-backed clock, so it can't know how long it was powered off,
> and its RTC drifts a few seconds/day. For true standalone accuracy add an I²C RTC
> (e.g. DS3231 + coin cell).

A host is still useful: whenever one is connected it re-syncs the clock to the exact time.

## Files

| File | Runs on | Purpose |
|------|---------|---------|
| `main.py` | the Pico | the clock itself |
| `charging.py` | the Pico | reads charger status and draws the bolt |
| `battery_log.py` | the Pico | records battery observations |
| `time_pusher.py` | your computer | sends the current time over USB serial |

## Install

1. Flash **MicroPython** for the RP2350 board and copy the Waveshare `lcd.py` display
   driver next to these files (it provides `LCD_1inch54`).
2. Copy the clock and battery modules to the board (e.g. with
   [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html)):
   ```bash
   mpremote connect /dev/ttyACM0 fs cp charging.py :charging.py
   mpremote connect /dev/ttyACM0 fs cp battery_log.py :battery_log.py
   mpremote connect /dev/ttyACM0 fs cp main.py :main.py
   mpremote connect /dev/ttyACM0 reset
   ```
3. On the host, run the time pusher:
   ```bash
   python3 time_pusher.py                    # auto-detects the serial port
   python3 time_pusher.py --port /dev/ttyACM0 --interval 5
   ```

The pusher has no dependencies (standard library only) and reconnects by itself if the
board is unplugged and plugged back in.

## Configuration

`time_pusher.py` options / environment:

| Env / flag | Default | Meaning |
|------------|---------|---------|
| `--port`, `PICO_PORT` | auto (`/dev/cu.usbmodem*`, `/dev/ttyACM*`) | serial device |
| `--interval` | `5` | seconds between updates |

## Notes

- The display driver (`lcd.py`) comes with the Waveshare demo and is **not** included here.
- `framebuf` on this MicroPython build has `ellipse()` but **no `circle()`** — useful to know
  if you extend the drawing code.
- The 240×240 framebuffer is ~115 KB, so keep the application lean (heap is ~138 KB free).
- If you later re-flash MicroPython, delete `clock.dat` if you want a clean start.

## License

MIT

## Battery usage log

The clock records voltage, ADC values and charger status in `battery_usage.csv` every
five minutes while running. The log stops growing at 256 KiB. Elapsed seconds reset
at boot; local clock time may be adjusted by USB sync. Charger status is not proof
that USB is disconnected. Copy the log from the board with `mpremote fs cp :battery_usage.csv battery_usage.csv`
for analysis. Voltage-based runtime forecasts
are approximate and require a substantial battery-only discharge record.
