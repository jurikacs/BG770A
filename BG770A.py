'''
	Finamon BG770A Library 
	Library for Finamon GNSS/Modem BG770A Shield.
'''

import serial
import sys
import time


bRPi = False
if "win" not in sys.platform: 
	import RPi.GPIO as GPIO
	bRPi = True



# Peripheral Pin Definations
RESET = 16

# global variables
TIMEOUT = 3 # seconds
ser = serial.Serial()

###########################################
### Private Methods #######################
###########################################

# function for printing debug message 
def debug_print(message):
	print(message)

# function for getting time as miliseconds
def millis():
	return int(time.time())

# function for delay as miliseconds
def delay(ms):
	time.sleep(float(ms/1000.0))

###########################################
### NB IoT Shield Class ################
###########################################	
class BG770A:
	board = ""			# Shield name
	ip_address = ""
	domain_name = ""
	port_number = ""
	timeout = TIMEOUT	# default timeout
	
	compose = ""
	response = ""

	
	# Default Initializer
	def __init__(self, serial_port="COM5", serial_baudrate=115200, board="Finamon GNSS/Modem BG770A Shield"):
		
		self.board = board
	
		ser.port = serial_port
		ser.baudrate = serial_baudrate
		ser.parity=serial.PARITY_NONE
		ser.stopbits=serial.STOPBITS_ONE
		ser.bytesize=serial.EIGHTBITS

		self.latitude = 0
		self.longitude = 0

		debug_print(self.board + " created")

		if not bRPi:
			return

		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		
		GPIO.setup(RESET,GPIO.OUT)
		GPIO.output(RESET,GPIO.LOW)

			
	# Function for clearing compose variable
	def clear_compose(self):
		self.compose = ""
		
	# Function for getting modem response
	def getResponse(self, desired_response):
		if (ser.isOpen() == False):
			ser.open()
			
		while 1:	
			self.response =""
			while(ser.inWaiting()):
				self.response += ser.read(ser.inWaiting()).decode('utf-8', errors='ignore')
			if(self.response.find(desired_response) != -1):
				debug_print(self.response)
				break

	# Function for sending at comamand to module
	def sendATcmdOnce(self, command):
		if (ser.isOpen() == False):
			ser.open()		
		self.compose = ""
		self.compose = str(command) + "\r"
		ser.reset_input_buffer()
		ser.write(self.compose.encode())
		debug_print(self.compose)

	# Function for sending at command to BG770A.
	def sendATcmd(self, command, desired_response, timeout = None):
		
		if timeout is None:
			timeout = self.timeout
			
		self.sendATcmdOnce(command)
		
		f_debug = False
		
		timer = millis()
		while 1:
			if( millis() - timer > timeout): 
				self.sendATcmdOnce(command)
				timer = millis()
				f_debug = False
			
			self.response =""
			while(ser.inWaiting()):
				try: 
					self.response += ser.read(ser.inWaiting()).decode('utf-8', errors='ignore')
					delay(100)
				except Exception as e:
					debug_print(e.Message)
				# debug_print(self.response)
					
			if(self.response.find(desired_response) != -1):
				debug_print(self.response)
				break

	# Function for saving conf. and reset BG770A module
	def resetModule(self):
		self.saveConfigurations()
		delay(200)
		self.sendATcmd("AT+NRB","")


	# Function for save configurations shield be done in current session. 
	def saveConfigurations(self):
		self.sendATcmd("AT&W","OK\r\n")

	# Function for getting IMEI number
	def getIMEI(self):
		return self.sendATcmd("AT+CGSN=1","OK\r\n")


	# Function for getting firmware info
	def getFirmwareInfo(self):
		return self.sendATcmd("AT+CGMR","OK\r\n")

	# Function for getting hardware info
	def getHardwareInfo(self):
		return self.sendATcmd("AT+CGMM","OK\r\n")

	# Function for setting autoconnect feature configuration 
	def setAutoConnectConf(self, autoconnect):
		self.compose = "AT+NCONFIG=AUTOCONNECT,"
		self.compose += autoconnect

		self.sendATcmd(self.compose,"OK\r\n")
		self.clear_compose()

	# Function for setting scramble feature configuration 
	def setScrambleConf(self, scramble):
		self.compose = "AT+NCONFIG=CR_0354_0338_SCRAMBLING,"
		self.compose += scramble

		self.sendATcmd(self.compose,"OK\r\n")
		self.clear_compose()

	# Function for getting self.ip_address
	def getIPAddress(self):
		return self.ip_address

	# Function for setting self.ip_address
	def setIPAddress(self, ip):
		self.ip_address = ip

	# Function for getting self.domain_name
	def getDomainName(self):
		return self.domain_name

	# Function for setting domain name
	def setDomainName(self, domain):
		self.domain_name = domain

	# Function for getting port
	def getPort(self):
		return self.port_number

	# Function for setting port
	def setPort(self, port):
		self.port_number = port

	# Function for getting timout in ms
	def getTimeout(self):
		return self.timeout

	# Function for setting timeout in ms    
	def setTimeout(self, new_timeout):
		self.timeout = new_timeout


	#******************************************************************************************
	#*** Network Service Functions ************************************************************
	#****************************************************************************************** 

	# Function for getting signal quality
	def getSignalQuality(self):
		return self.sendATcmd("AT+CSQ","OK\r\n")

	# Function for connecting to base station of operator
	def connectToOperator(self):
		debug_print("Trying to connect base station of operator...")
		self.sendATcmd("AT+CGATT=0","OK\r\n",8) # with 8 seconds timeout
		delay(1000)
		self.sendATcmd("AT+CGATT=1","OK\r\n",8) # with 8 seconds timeout
		delay(2000)
		debug_print("Wait until getting <CGATT:1> response..." )
		self.sendATcmd("AT+CGATT?","+CGATT:1\r\n")


	#******************************************************************************************
	#*** UDP Protocols Functions ********************************************************
	#******************************************************************************************
	
	# Function for connecting to server via UDP
	def startUDPService(self):
		port = "3005"

		self.compose = "AT+NSOCR=DGRAM,17,"
		self.compose += str(self.port_number)
		self.compose += ",0"

		self.sendATcmd(self.compose,"OK\r\n")
		self.clear_compose()

	# Fuction for sending data via udp.
	def sendDataUDP(self, data):
		self.compose = "AT+NSOST=0,"
		self.compose += str(self.ip_address)
		self.compose += ","
		self.compose += str(self.port_number)
		self.compose += ","
		self.compose += str(len(data))
		self.compose += ","
		self.compose += data.encode("utf-8").hex() #hex(data)

		self.sendATcmd(self.compose,"\r\n")
		self.clear_compose()

	# Function for closing server connection
	def closeConnection(self):
		self.sendATcmd("AT+NSOCL=0","\r\n")
			


	#******************************************************************************************
	#*** GNSS Functions ******************************************************************
	#******************************************************************************************

	def gnssOn(self):
	    pass

	def gnssOff(self):
	    pass

	def updateGnssLocation(self):
		return [self.latitude, self.longitude]

	def getSatellitesInfo(self):
	    pass



if __name__=='__main__':

	import serial.tools.list_ports
	ports = list(serial.tools.list_ports.comports())
	for p in ports:
		print(p)

	module = BG770A()

	module.sendATcmd("ATE1","OK\r\n")
	module.gnssOn();
	module.updateGnssLocation();
