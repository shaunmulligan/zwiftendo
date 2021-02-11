## Zwiftendo

> Warning!!! this is still very much a work in progress.

Zwiftendo is a basic BLE keyboard to control the Zwift indoor cycling game from your bike handlebars. It is based on the [Adafruit Feather nRF52840 Express](https://www.adafruit.com/product/4062) and uses a [Pimoroni Trackball](https://shop.pimoroni.com/products/trackball-breakout) for the input.

### Required CircuitPython Libs:

To run correctly, this code needs you to have a copy of the following libraries in the `/lib` folder on `CIRCUITPYTHON` drive. 

- adafruit_ble (https://github.com/adafruit/Adafruit_CircuitPython_BLE)
- adafruit_hid (https://github.com/adafruit/Adafruit_CircuitPython_HID)

### Usage:

Connect the nRF52840 Express to your laptop and copy code.py, pimoroni_trackball.py and the above mentioned libraries to the CIRCUITPYTHON drive. Connect up the Trackball i2c pins to the nRF53840 SCL and SDA pins. Make sure to add a 10k pull-up resistor as there are no internal ones on the i2c bus.

Once powered up, the device will be discoverable as a bluetooth keyboard called Zwiftendo. Once paired, the green LED at the centre of the trackball will turn blue and now when you swipe up and down it will scroll your screen up and down. Swiping right will skip your media forward and pushing the central button should play or pause your media.