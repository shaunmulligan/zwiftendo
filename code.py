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
from analogio import AnalogIn
import neopixel_write
from pimoroni_trackball import Trackball

# Setup onboard neopixel and set to off state
pixel = DigitalInOut(board.NEOPIXEL)
pixel.direction = Direction.OUTPUT
pixel_bat_low = bytearray([0, 100, 0])
pixel_off = bytearray([0, 0, 0])
neopixel_write.neopixel_write(pixel, pixel_off)

# Setup battery voltage level ADC pin
vbat_voltage = AnalogIn(board.VOLTAGE_MONITOR)

# Setup i2c bus and trackball instance
i2c = I2C() 
trackball = Trackball( i2c )
trackball.set_rgbw(0, 254, 0, 0)

# Setup button 1 (startBtn) on digital pin 9
startBtn = DigitalInOut(board.D9)
startBtn.direction = Direction.INPUT
startBtn.pull = Pull.UP

# Setup button 2 (btn2) on digital pin 10
btn2 = DigitalInOut(board.D10)
btn2.direction = Direction.INPUT
btn2.pull = Pull.UP

# Setup button 3 (btn3) on digital pin 11
btn3 = DigitalInOut(board.D11)
btn3.direction = Direction.INPUT
btn3.pull = Pull.UP

# Setup button 4 (btn4) on digital pin 12
btn4 = DigitalInOut(board.D12)
btn4.direction = Direction.INPUT
btn4.pull = Pull.UP

# Setup button 5 (btn2) on digital pin 13
btn5 = DigitalInOut(board.D13)
btn5.direction = Direction.INPUT
btn5.pull = Pull.UP

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

def get_bat_percent(pin):
    # percentage relavtive to 4.2V max
    return (((pin.value * 3.3) / 65536 * 2)/4.2)*100

if ble.connected:
    for c in ble.connections:
        c.disconnect()

print("Advertising...")
ble.start_advertising(advertisement, scan_response)

consumer_control = ConsumerControl(hid.devices)
k = Keyboard(hid.devices)
kl = KeyboardLayoutUS(k)
while True:

    while not ble.connected:
        pass
    print("Zwiftendo Running:")
    while ble.connected:
        # Check battery level
        bat_level = get_bat_percent(vbat_voltage)
        # Update bluetooth battery level prop
        bat.level = int(bat_level)
        # If battery is below 15% light up neopixel red
        if bat_level < 15:
            neopixel_write.neopixel_write(pixel, pixel_bat_low)
        # Set trackball Led Blue now that we are connected   
        trackball.set_rgbw(0, 0, 254, 0)
        up, down, left, right, switch, state = trackball.read()
        if not startBtn.value:
            # If we get a start, trigger applescript on laptop with key combo `ctrl`+`shift`+`=`.
            k.send(Keycode.CONTROL, Keycode.SHIFT, Keycode.EQUALS)
        if not btn2.value:
            # Play or Pause media
            consumer_control.send(ConsumerControlCode.PLAY_PAUSE)
        if not btn3.value:
            # Skip to next track on media
            consumer_control.send(ConsumerControlCode.SCAN_NEXT_TRACK)
        if not btn4.value:
            # Press space bar to trigger powerUp
            k.send(Keycode.SPACEBAR)
        if not btn5.value:
            # Press TAB to skip workout block
            k.send(Keycode.TAB)
        # Logic for Trackball controller
        if state:
            # Press enter
            k.send(Keycode.ENTER)
        if left > 10:
            # Press up arrow key
            k.send(Keycode.UP_ARROW)
        if right > 10:
            # Press down arrow key
            k.send(Keycode.DOWN_ARROW)
        if down > 10:
            # Press left arrow key
            k.send(Keycode.LEFT_ARROW)
        if up > 10:
            k.send(Keycode.RIGHT_ARROW)
        
        time.sleep(0.1)
    
    # If we get disconnected, go back to advertising and light trackball LED green
    ble.start_advertising(advertisement)
    trackball.set_rgbw(0, 254, 0, 0)