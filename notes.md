## ToDo:
- convert trackball.py to mpy to reduce resource usage: https://learn.adafruit.com/micropython-for-samd21/frozen-modules 

## Bluetooth HID:
- Media controls: https://github.com/adafruit/Adafruit_CircuitPython_HID/blob/master/adafruit_hid/consumer_control_code.py#L32
- Arrow control: https://github.com/adafruit/Adafruit_CircuitPython_HID/blob/master/adafruit_hid/keycode.py#L210

Tried these two below on micropython esp32 but dont seem to work. I can get macOS to see it as a keyboard but can't send any keystrokes.
* example here: https://github.com/micropython/micropython/pull/6559/files
* here: https://gitee.com/walkline/esp32-ble/blob/master/ble/ble_hid.py which seems to be using: https://gitee.com/walkline/micropython-ble-library 

## Trackball:
Found this repo and pulled the trackball module from it: https://github.com/mchobby/esp8266-upy/blob/master/trackball/lib/trackball.py
Had to fix it up a bit to get running on esp32 micropython, not sure if the interrupt stuff works yet but should be easy enough to get going. Took a little bit of trial and error to figure out the i2c bus, had to define the pins D22 and D23 in the i2c constructor.

Then rewrote it for circuitpython and created the pimoroni_trackball.py module. It was easy once I figured out the `adafruit_register` module to read and write to `i2c` registers.

## Useful mPy commands:
connect to wifi:
```
import boot
connect()
```

list modules
```
>>> help('modules')
```

list files
```
>>> import os                                                                   
>>> os.listdir() 
```