# Clock — Waveshare RP2350-Touch-LCD-1.54 (MicroPython)
#
# Just the time. The Pico has no RTC/WiFi, so the Mac sends the date/time over USB serial:
#     S|DT:YYYY-MM-DD:HH:MM:SS:WD|TS:HH:MM:SS
import gc
import select
import sys
import time

import framebuf
from machine import RTC
from lcd import LCD_1inch54

WHITE = 0xFFFF
BG    = 0x0841
DIM   = 0x4A69
CYAN  = 0x07FF
BLUE  = 0x249F          # bright blue for the weekday

DOW = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
MON = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

TIME_FILE = "clock.dat"        # last known time, so the clock survives a power cycle


def save_time():
    t = time.localtime()
    try:
        with open(TIME_FILE, "w") as f:
            f.write("%d,%d,%d,%d,%d,%d,%d" % (t[0], t[1], t[2], t[3], t[4], t[5], t[6]))
    except Exception:
        pass


def load_time():
    """Restore the RTC from flash at boot. Returns True if a saved time was found."""
    try:
        with open(TIME_FILE) as f:
            p = f.read().strip().split(",")
        rtc.datetime((int(p[0]), int(p[1]), int(p[2]), int(p[6]),
                      int(p[3]), int(p[4]), int(p[5]), 0))
        return True
    except Exception:
        return False


gc.collect()
lcd = LCD_1inch54()
rtc = RTC()
time_set = load_time()   # resume from the last saved time if we have one

poll = select.poll()
poll.register(sys.stdin, select.POLLIN)

_glyph = bytearray(8 * 8 * 2)
_gfb = framebuf.FrameBuffer(_glyph, 8, 8, framebuf.RGB565)


def text(s, x, y, scale, color):
    for i, ch in enumerate(s):
        _gfb.fill(BG)
        _gfb.text(ch, 0, 0, color)
        cx = x + i * 8 * scale
        for yy in range(8):
            for xx in range(8):
                if _gfb.pixel(xx, yy) != BG:
                    lcd.fill_rect(cx + xx * scale, y + yy * scale, scale, scale, color)


def ctext(s, y, scale, color):
    text(s, max(0, (240 - len(s) * 8 * scale) // 2), y, scale, color)


def draw_clock():
    lcd.fill(BG)
    if not time_set:
        ctext("CLOCK", 40, 3, CYAN)
        ctext("syncing...", 120, 2, DIM)
    else:
        t = time.localtime()
        ctext("%02d:%02d:%02d" % (t[3], t[4], t[5]), 62, 3, WHITE)
        ctext("%02d %s %d" % (t[2], MON[t[1] - 1], t[0]), 128, 2, CYAN)
        ctext(DOW[t[6]], 162, 2, BLUE)
    lcd.show()


def handle(line):
    global time_set
    line = line.strip()
    if not (line.startswith("S|") or line.startswith("F|")):
        return False
    for part in line.split("|")[1:]:
        f = part.split(":")
        if f[0] == "DT":
            try:
                y, mo, d = f[1].split("-")
                rtc.datetime((int(y), int(mo), int(d), int(f[5]),
                              int(f[2]), int(f[3]), int(f[4]), 0))
                time_set = True
                save_time()
            except Exception:
                pass
    return True


gc.collect()
draw_clock()
_tick = time.time()
_saved_min = time.localtime()[4]
while True:
    if poll.poll(0):
        try:
            line = sys.stdin.readline()
        except Exception:
            line = ""
        if line and handle(line):
            print("K")
            draw_clock()
    now = time.time()
    if now - _tick >= 1.0:
        _tick = now
        draw_clock()
        if time_set and time.localtime()[4] != _saved_min:   # once a minute: persist the time
            _saved_min = time.localtime()[4]
            save_time()
    time.sleep_ms(50)
