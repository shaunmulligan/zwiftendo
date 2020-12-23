## ToDo:
- implement bluetooth HID
- convert trackball.py to mpy to reduce resource usage: https://learn.adafruit.com/micropython-for-samd21/frozen-modules 

## Bluetooth HID:

example here: https://github.com/micropython/micropython/pull/6559/files
and here:
https://gitee.com/walkline/esp32-ble/blob/master/ble/ble_hid.py which seems to be using: https://gitee.com/walkline/micropython-ble-library

## Trackball:
found this repo and pulled the trackball module from it: https://github.com/mchobby/esp8266-upy/blob/master/trackball/lib/trackball.py

Had to fix it up a bit to get running, not sure if the interrupt stuff works yet but should be easy enough to get going.

Took a little bit of trial and error to figure out the i2c bus, had to define the pins D22 and D23 in the i2c constructor.

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