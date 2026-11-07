from machine import Pin

_status = Pin(17, Pin.IN, Pin.PULL_UP)

def is_charging():
    return _status.value() == 0

def draw(lcd, color, x, y):
    if is_charging():
        lcd.line(x + 4, y, x + 1, y + 4, color)
        lcd.line(x + 1, y + 4, x + 4, y + 4, color)
        lcd.line(x + 4, y + 4, x + 2, y + 8, color)
        lcd.line(x + 2, y + 8, x + 7, y + 3, color)
        lcd.line(x + 7, y + 3, x + 4, y + 3, color)
        lcd.line(x + 4, y + 3, x + 5, y, color)
        lcd.line(x + 5, y, x + 4, y, color)
