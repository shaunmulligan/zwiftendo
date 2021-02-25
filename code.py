
"""
Zwiftendo is a bluetooth keyboard for controlling zwift and music
"""

# import libs
import board
import busio
from analogio import AnalogIn
from micropython import const

from adafruit_seesaw.seesaw import Seesaw
from adafruit_debouncer import Debouncer
import tasko # From https://github.com/WarriorOfWire/tasko

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

# Define buttons to pin mapping
BUTTON_A = const(6)
BUTTON_B = const(7)
BUTTON_Y = const(9)
BUTTON_X = const(10)
BUTTON_SEL = const(14)

# Setup battery voltage level ADC pin
vbat_voltage = AnalogIn(board.VOLTAGE_MONITOR)

# Setup our i2c but to the Joy Feather
i2c_bus = busio.I2C(board.SCL, board.SDA)
ss = Seesaw(i2c_bus)

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

# Teardown any other BLE connections
if ble.connected:
    for c in ble.connections:
        c.disconnect()

# Start advertising on BLE
print("Advertising...")
ble.start_advertising(advertisement, scan_response)

# Setup bluetooth HID resources
consumer_control = ConsumerControl(hid.devices)
k = Keyboard(hid.devices)
kl = KeyboardLayoutUS(k)

def make_pin_reader(pin):
    """ Creates a pin reader to feed to Debouncer """
    ss.pin_mode(pin, ss.INPUT_PULLUP)
    return lambda: ss.digital_read(pin)

def get_bat_percent(pin):
    # percentage relavtive to 4.2V max
    return (((pin.value * 3.3) / 65536 * 2)/4.2)*100

# Create debounced button inputs
btnA = Debouncer(make_pin_reader(BUTTON_A))
btnB = Debouncer(make_pin_reader(BUTTON_B))
btnX = Debouncer(make_pin_reader(BUTTON_X))
btnY = Debouncer(make_pin_reader(BUTTON_Y))
btnSel = Debouncer(make_pin_reader(BUTTON_SEL))

# Global state for x,y of joystick :/
last_x = 0
last_y = 0

async def read_joy_stick():
    """ Read the joystick and send UP,DOWN,LEFT,RIGHT commands"""
    global last_x
    global last_y
    x = ss.analog_read(2)
    y = ss.analog_read(3)
 
    if (abs(x - last_x) > 40) or (abs(y - last_y) > 40):
        last_x = x
        last_y = y
        if y > 1000:      
            if ble.connected: k.send(Keycode.RIGHT_ARROW)
            print("RIGHT")
        if y < 30:
            if ble.connected: k.send(Keycode.LEFT_ARROW)
            print("LEFT")
        if x > 1000:
            if ble.connected: k.send(Keycode.DOWN_ARROW)
            print("DOWN")
        if x < 30:
            if ble.connected: k.send(Keycode.UP_ARROW)
            print("UP")
    
    # await tasko.sleep(1)  # use to wait/sleep in a non-blocking manner

async def read_buttons():
    """ Scan the buttons on falling edge and send commands """
    btnA.update()
    btnB.update()
    btnX.update()
    btnY.update()
    btnSel.update()
    if btnA.fell:
        # Send ENTER/RETURN if BLE connected
        if ble.connected: k.send(Keycode.ENTER)
        print('A Fell')
    if btnB.fell:
        # Skip to next track on media if connected via BLE
        if ble.connected: consumer_control.send(ConsumerControlCode.SCAN_NEXT_TRACK)
        print('B Fell')
    if btnX.fell:
        # TODO: allow this to be toggled for race or training mode
        # Press TAB to skip workout block
        if ble.connected: k.send(Keycode.TAB)
        print('X Fell')
    if btnY.fell:
        # Play or Pause current media
        consumer_control.send(ConsumerControlCode.PLAY_PAUSE)
        print('Y Fell')
    if btnSel.fell:
        # If we get a start, trigger applescript on laptop with key combo `ctrl`+`shift`+`=`.
        if ble.connected: k.send(Keycode.CONTROL, Keycode.SHIFT, Keycode.EQUALS)
        print('Select Fell')

async def update_battery_state():
    """ Update the battery level status """
    # Check battery level
    bat_level = get_bat_percent(vbat_voltage)
    print("Battery Level: ", bat_level)
    # Update bluetooth battery level prop
    bat.level = int(bat_level)

async def check_ble_connection():
    if not ble.connected and not ble.advertising:
        # Start advertising on BLE
        print("Disconnected going back to advertising...")
        ble.start_advertising(advertisement, scan_response)

# Schedule the workflows at whatever frequency makes sense
tasko.schedule(hz=7,  coroutine_function=read_joy_stick)
tasko.schedule(hz=15,  coroutine_function=read_buttons)
tasko.schedule(hz=1/5, coroutine_function=check_ble_connection)
tasko.schedule(hz=1/60, coroutine_function=update_battery_state)
# And let tasko do while True
tasko.run()