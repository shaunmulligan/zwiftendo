"""
This is a CircuitPython module for Pimoroni trackball breadkout https://shop.pimoroni.com/products/trackball-breakout .
Originally adapted from https://github.com/mchobby/esp8266-upy/blob/master/trackball/lib/trackball.py
"""

import time, struct

from adafruit_register.i2c_struct import UnaryStruct
from adafruit_register.i2c_struct_array import StructArray
from adafruit_bus_device import i2c_device

class Trackball(object):
    """
    Initialise the Trackball chip at ``address`` on ``i2c_bus``.
    :param ~busio.I2C i2c_bus: The I2C bus which the Trackball is connected to.
    :param int address: The I2C address of the Trackball.

    Usage:

        import time
        from board import I2C
        from pimoroni_trackball import Trackball

        i2c = I2C() 

        trackball = Trackball( i2c )

        trackball.set_rgbw(0, 127, 127, 0)

        r, g, b, w = trackball.rgbw
        print("Red: {:02d} Green: {:02d} Blue: {:02d} White: {:02d}".format(r,g,b,w))
        while True:
            up, down, left, right, switch, state = trackball.read()
            print("r: {:02d} u: {:02d} d: {:02d} l: {:02d} switch: {:03d} state: {}".format(right, up, down, left, switch, state))
            time.sleep(0.200)

    """
    CHIP_ID  =  0xBA11

    # Registers:
    # LEDs
    REG_LED_RED  =  UnaryStruct(0x00, "<B")
    REG_LED_GRN  =  UnaryStruct(0x01, "<B")
    REG_LED_BLU  =  UnaryStruct(0x02, "<B")
    REG_LED_WHT  =  UnaryStruct(0x03, "<B")
   
    # Directions
    REG_LEFT  =  UnaryStruct(0x04, "<B")
    REG_RIGHT  =  UnaryStruct(0x05, "<B")
    REG_UP  =  UnaryStruct(0x06, "<B")
    REG_DOWN  =  UnaryStruct(0x07, "<B")
    REG_SWITCH  =  UnaryStruct(0x08, "<B")

    # Misc
    REG_INT  =  UnaryStruct(0xF9, "<B")
    # TODO: maybe use CTRL reg + MSK_CTRL_RESET to reset the device on teardown?
    REG_CHIP_ID_L  =  UnaryStruct(0xFA, "<B")
    REG_CHIP_ID_H  =  UnaryStruct(0xFB, "<B")

    # Bit Masks:
    MSK_SWITCH_STATE  =  0b10000000
    MSK_INT_TRIGGERED  =  0b00000001
    MSK_INT_OUT_EN  =  0b00000010
    MSK_CTRL_SLEEP  =  0b00000001
    MSK_CTRL_RESET  =  0b00000010
    MSK_CTRL_FREAD  =  0b00000100
    MSK_CTRL_FWRITE  =  0b00001000

    def __init__(self, i2c_bus, address = 0x0A , timeout = 5):
        self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)
        self._timeout  =  timeout
        
        chip_id = (self.REG_CHIP_ID_H << 8) + self.REG_CHIP_ID_L
        if  chip_id  !=  self.CHIP_ID:
            raise  Exception ( "Invalid chip ID: 0x {: 04X}, expected 0x {: 04X}" . format ( chip_id , self.CHIP_ID ))

        self.enable_interrupt()

    def enable_interrupt(self, interrupt=True):
        value  =  self.REG_INT
        value  =  value  & ( 0xFF  ^  self.MSK_INT_OUT_EN )
        if  interrupt:
            value  =  value  |  self.MSK_INT_OUT_EN
        self.REG_INT = value
    
    def get_interrupt( self ):
        """Get the trackball interrupt status."""
        # Only support the software version
        data  =  self.REG_INT
        return ( data &  self.MSK_INT_TRIGGERED ) == self.MSK_INT_TRIGGERED
    
    def _wait_for_flash(self):
        t_start  =  time.time()
        while  self.get_interrupt():
            if  time.time() -  t_start  >  self._timeout:
                raise  RuntimeError ( "Timed out waiting for interrupt!" )
            time.sleep( 0.001 )

        t_start  = time.time()
        while  not  self.get_interrupt():
            if  time.time() -  t_start  >  self._timeout :
                raise  RuntimeError ( "Timed out waiting for interrupt!" )
            time.sleep( 0.001 )

    def set_red( self , value ):
        """Set brightness of trackball red LED."""
        self.REG_LED_RED = value  &  0xff

    def set_green( self , value ):
        """Set brightness of trackball green LED."""
        self.REG_LED_GRN = value  &  0xff

    def set_blue( self , value ):
        """Set brightness of trackball blue LED."""
        self.REG_LED_BLU = value  &  0xff

    def set_white( self , value ):
        """Set brightness of trackball white LED."""
        self.REG_LED_WHT = value  &  0xff
    
    @property
    def rgbw(self):
        return self.REG_LED_RED, self.REG_LED_GRN, self.REG_LED_BLU, self.REG_LED_WHT
    
    def set_rgbw(self, r, g, b, w):
        """Set all LED brightness as RGBW."""
        self.set_red(r)
        self.set_green(g)
        self.set_blue(b)
        self.set_white(w)

    def read( self ):
        """Read up, down, left, right and switch data from trackball."""
        switch , switch_state  =  self.REG_SWITCH  & ( 0xFF  ^  self.MSK_SWITCH_STATE ), ( self.REG_SWITCH  &  self.MSK_SWITCH_STATE ) == self.MSK_SWITCH_STATE
        return  self.REG_UP , self.REG_DOWN , self.REG_LEFT , self.REG_RIGHT , switch , switch_state

    def reset(self):
        """Reset the chip."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.deinit()

    def deinit(self):
        """Stop using the trackball."""
        self.reset()