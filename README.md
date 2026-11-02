# pico-cuadrat-rellotge

A tiny **MicroPython clock** for the **Waveshare RP2350-Touch-LCD-1.54** (round 240×240).

```
     23:59:27        ← time      (white)
     02 Nov 2026     ← date      (cyan)
       Monday        ← weekday   (blue)
```

## Why a helper script is needed

This board has **no WiFi and no battery-backed RTC**, so the Pico cannot know the time by
itself. A host (Mac/Linux/Windows) sends the date & time over the **USB serial** link every
few seconds; the Pico stores it in its RTC and ticks the seconds locally in between.

```
host  --"S|DT:YYYY-MM-DD:HH:MM:SS:WD|TS:HH:MM:SS"-->  Pico (USB CDC)
Pico  <--"K" (acknowledgement)------------------------
```

## Files

| File | Runs on | Purpose |
|------|---------|---------|
| `main.py` | the Pico | the clock itself |
| `time_pusher.py` | your computer | sends the current time over USB serial |

## Install

1. Flash **MicroPython** for the RP2350 board and copy the Waveshare `lcd.py` display
   driver next to these files (it provides `LCD_1inch54`).
2. Copy `main.py` to the board as `main.py` (e.g. with
   [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html)):
   ```bash
   mpremote connect /dev/ttyACM0 fs cp main.py :main.py
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

## License

MIT
