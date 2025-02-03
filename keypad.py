# - Title: Macro Keypad Controller (main)
# - Description: Scan through buttons in a matrix button
#                layout and send a preconfigured keycode to
#                the connected device
# - Author: Caseyr
# - Date Created: 2025.1.23
# - Last Modified: 2025.2.3

# Mostly follows the keyboard implementation from the micropython-lib example for the actual sending-data bit
# https://github.com/micropython/micropython-lib/blob/master/micropython/usb/examples/device/keyboard_example.py

#### Imports ####
import utime, usb.device
from machine import I2C, Pin
# https://github.com/micropython/micropython-lib/blob/master/micropython/usb/usb-device/usb/device/core.py
from usb.device import core
# https://github.com/micropython/micropython-lib/blob/master/micropython/usb/usb-device-keyboard/usb/device/keyboard.py
from usb.device.keyboard import KeyboardInterface as KI
from usb.device.keyboard import KeyCode as KC
# https://github.com/dhylands/python_lcd/blob/master/lcd/lcd_api.py
from lcd_api import LcdApi
# https://github.com/T-622/RPI-PICO-I2C-LCD/blob/main/pico_i2c_lcd.py
from pico_i2c_lcd import I2cLcd

#### Variables ####
start_time = utime.time()
board_led = Pin(25, Pin.OUT)
timestep = 50

cols = [Pin(20, Pin.OUT), Pin(19, Pin.OUT), Pin(18, Pin.OUT), Pin(17, Pin.OUT), Pin(16, Pin.OUT)]
rows = [Pin(11, Pin.IN, Pin.PULL_UP), Pin(12, Pin.IN, Pin.PULL_UP), Pin(13, Pin.IN, Pin.PULL_UP)]

# Initialize pins to off
for col in cols:
    col.off()

KEYS = [
    [KC.F13, KC.F14, KC.F15, KC.F16, KC.F17],
    [KC.F18, KC.F19, KC.F20, KC.F21, KC.F22],
    [KC.F23, KC.F24, KC.X, KC.Z, KC.LEFT_SHIFT],
]

matrix_pressed = [[0 for i in range(5)] for j in range(3)]

#### Displays ####

#### Definitions ####
I2C_NROW = 4
I2C_NCOL = 20
display_update = start_time

# Initialize a given display address per device at the given sda and scl pins
class Display:
    def __init__(self, address, sda, scl):
        i2c = I2C(0, sda=sda, scl=scl, freq=100000)
        self.lcd = I2cLcd(i2c, address, I2C_NROW, I2C_NCOL)
        self.last_time = 0
        
    def blit(self, delay, msg="debug"):
        # Default timestep updates time display 5/s
        if utime.ticks_ms() - self.last_time > delay * 10:
            self.last_time = utime.ticks_ms()
            self.lcd.move_to(0,1)
            self.lcd.putstr(msg[0])
            self.lcd.move_to(0,2)
            self.lcd.putstr(msg[1])
            self.lcd.move_to(0,3)
            self.lcd.putstr(msg[2])

# Initialize LCD display on pins 0 and 1
sda = Pin(0, Pin.OUT)
scl = Pin(1, Pin.OUT)
display = Display(0x27, sda, scl)
display.lcd.clear()
display.lcd.move_to(0,0)
display.lcd.putstr("Reading...")

# Initialize and re-enumerate keyboard interface
k = KI()
core.get().init(k, builtin_driver=True)

keys = []
prev_keys = [None]

def main():
    while True:
        scanKeys()
        messages = ["", "", ""]
        keys.clear()
        if k.is_open():
            for col in range(len(cols)):
                for row in range(len(rows)):
                    messages[row] += str(matrix_pressed[row][col])
                    
                    if matrix_pressed[row][col]:
                        keys.append(KEYS[row][col])
                    
            if keys != prev_keys:
                k.send_keys(keys)
                prev_keys.clear()
                prev_keys.extend(keys)
        display.blit(timestep, messages)

# Return map of 
def scanKeys():
    for col in range(len(cols)):
        cols[col].on()
        for row in range(len(rows)):
            matrix_pressed[row][col] = rows[row].value()
        cols[col].off()
        utime.sleep_ms(1)

main()
