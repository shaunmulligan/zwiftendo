"""
This example acts as a keyboard to peer devices.
"""

# import board
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
from pimoroni_trackball import Trackball

# Setup i2c bus and trackball instance
i2c = I2C() 
trackball = Trackball( i2c )
trackball.set_rgbw(0, 254, 0, 0)

# Use default HID descriptor
hid = HIDService()
bat = BatteryService()
device_info = DeviceInfoService(
    software_revision=adafruit_ble.__version__, manufacturer="Adafruit Industries"
)
advertisement = ProvideServicesAdvertisement(hid)
advertisement.appearance = 961
scan_response = Advertisement()

ble = adafruit_ble.BLERadio()
ble.name = "hoodlum"
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
    print("Hoodlum Running:")
    while ble.connected:
        trackball.set_rgbw(0, 0, 254, 0)
        up, down, left, right, switch, state = trackball.read()
        if state:
            consumer_control.send(ConsumerControlCode.PLAY_PAUSE)
        if up > 10:
            consumer_control.send(ConsumerControlCode.SCAN_NEXT_TRACK)
        if left > 10:
            k.send(Keycode.UP_ARROW)
        if right > 10:
            k.send(Keycode.DOWN_ARROW)
        
        time.sleep(0.2)
    ble.start_advertising(advertisement)
    trackball.set_rgbw(0, 254, 0, 0)