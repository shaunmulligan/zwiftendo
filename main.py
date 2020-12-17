from  machine  import  I2C, Pin
from  trackball  import  Trackball
import  time

# Huzzah32 i2c pins are on D22 and D23
i2c = I2C(1, scl=Pin(22), sda=Pin(23))

# initialize the trackball
trackball  =  Trackball ( i2c )
trackball . set_rgbw ( 0 , 0 , 255 , 0 )

while  True :
	up , down , left , right , switch , state  =  trackball . read ()
	print ( "r: {: 02d} u: {: 02d} d: {: 02d} l: {: 02d} switch: {: 03d} state: {}" . format ( right , up , down , left , switch , state ))
	time . sleep ( 0.200 )