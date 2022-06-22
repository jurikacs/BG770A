# Distributed with a free-will license.
# This code is designed to work with Finamon GNSS/Modem BG770A Shield

import sys
import time

bRPi = False
if "win" not in sys.platform: 
	import smbus
	import RPi.GPIO as GPIO
	bRPi = True

# Peripheral Pin Definations SixFab
#USER_BUTTON = 21  
#USER_LED = 20

# Peripheral Pin Definations Finamon
USER_BUTTON = 27  
USER_LED = 22

VDD_EXT = 6
LUX_CHANNEL = 0


class board_hw:

	def __init__(self):
		if not bRPi:
			return
		# Get I2C bus
		self.bus = smbus.SMBus(1)
		time.sleep(0.5)
		
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)

	def readAcc(self):
		return
	
	# Function for reading temperature
	def readTemp(self):
		return

	# Function for reading user button
	def readUserButton(self):
		GPIO.setup(USER_BUTTON, GPIO.IN, pull_up_down = GPIO.PUD_UP)
		return GPIO.input(USER_BUTTON)

	# Function for turning on user LED
	def turnOnUserLED(self):
		if not bRPi:
			return
		GPIO.setup(USER_LED, GPIO.OUT)
		GPIO.output(USER_LED, 1)

	# Function for turning off user LED
	def turnOffUserLED(self):
		if not bRPi:
			return
		GPIO.setup(USER_LED, GPIO.OUT)
		GPIO.output(USER_LED, 0)




if __name__=='__main__':

    shield = board_hw()

    for i in range (10):
        print("user LED ON") 
        shield.turnOnUserLED()
        time.sleep(1)

        print("user LED OFF") 
        shield.turnOffUserLED()
        time.sleep(1)

    while(True):
        if shield.readUserButton():
            shield.turnOffUserLED()
        else:
            shield.turnOnUserLED()
