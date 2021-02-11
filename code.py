"""
Zwiftendo is a bluetooth keyboard for controlling zwift and music
"""
import sys
import time

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keycode import Keycode

import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_ble.services.standard import BatteryService

from board import I2C
import board
from digitalio import DigitalInOut, Direction, Pull
from pimoroni_trackball import Trackball

# Setup i2c bus and trackball instance
i2c = I2C() 
trackball = Trackball( i2c )
trackball.set_rgbw(0, 254, 0, 0)

# Setup button 1 (btn1) on digital pin 9
btn1 = DigitalInOut(board.D9)
btn1.direction = Direction.INPUT
btn1.pull = Pull.UP

# Setup button 2 (btn2) on digital pin 10
btn2 = DigitalInOut(board.D10)
btn2.direction = Direction.INPUT
btn2.pull = Pull.UP

# Use default HID descriptor
hid = HIDService()
bat = BatteryService()
# device_info seems to throw an error on circuitpython v6.1.0+beta2
# device_info = DeviceInfoService(
#     software_revision=adafruit_ble.__version__, manufacturer="Adafruit Industries"
# )
advertisement = ProvideServicesAdvertisement(hid)
advertisement.appearance = 961
scan_response = Advertisement()
ble = adafruit_ble.BLERadio()
ble.name = "Zwiftendo"

# TODO: move battery checking to loop
bat.level = 69
if ble.connected:
    for c in ble.connections:
        c.disconnect()

print("advertising")
ble.start_advertising(advertisement, scan_response)

consumer_control = ConsumerControl(hid.devices)
k = Keyboard(hid.devices)
kl = KeyboardLayoutUS(k)
while True:
    while not ble.connected:
        pass
    print("Zwiftendo Running:")
    while ble.connected:
        trackball.set_rgbw(0, 0, 254, 0)
        up, down, left, right, switch, state = trackball.read()
        if state:
            # Press enter
            k.send(Keycode.ENTER)
        if not btn2.value:
            # Play or Pause media
            consumer_control.send(ConsumerControlCode.PLAY_PAUSE)
        if not btn1.value:
            # Skip to next track on media
            consumer_control.send(ConsumerControlCode.SCAN_NEXT_TRACK)
        if up > 10:
            # Press up arrow key
            k.send(Keycode.UP_ARROW)
        if down > 10:
            # Press down arrow key
            k.send(Keycode.DOWN_ARROW)
        if left > 10:
            # Press left arrow key
            k.send(Keycode.LEFT_ARROW)
        if right > 10:
            k.send(Keycode.RIGHT_ARROW)
        
        time.sleep(0.1)
    ble.start_advertising(advertisement)
    trackball.set_rgbw(0, 254, 0, 0)