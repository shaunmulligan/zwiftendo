## Trackball:
found this repo and pulled the trackball module from it: https://github.com/mchobby/esp8266-upy/blob/master/trackball/lib/trackball.py

Had to fix it up a bit to get running, not sure if the interrupt stuff works yet but should be easy enough to get going.

Took a little bit of trial and error to figure out the i2c bus, had to define the pins D22 and D23 in the i2c constructor.

## Useful mPy commands:

list modules
```
>>> help('modules')
```

list files
```
>>> import os                                                                   
>>> os.listdir() 
```