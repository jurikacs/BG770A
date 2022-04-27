'''
	Finamon BG770A Library 
	Library for Finamon GNSS/Modem BG770A Shield.
'''

import csv
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
TIMEOUT = 1.0 # seconds
ser = serial.Serial()

###########################################
### Private Methods #######################
###########################################

# function for printing debug message 
def debug_print(message):
	print(message)
	#print(time.time(), message)

# function for getting time as miliseconds
def millis():
	return int(time.time()*1000)

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

	latitude = 0
	longitude = 0
		
	# Default Initializer
	def __init__(self, serial_port="COM4", serial_baudrate=115200, board="Finamon GNSS/Modem BG770A Shield"):
		
		self.board = board
	
		ser.port = serial_port
		ser.baudrate = serial_baudrate
		ser.parity=serial.PARITY_NONE
		ser.stopbits=serial.STOPBITS_ONE
		ser.bytesize=serial.EIGHTBITS


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

	# Function for sending at command to BG770A.
	def sendATcmd(self, command, desired_response = "OK\r\n", timeout_s = None):
		
		if timeout_s is None:
			timeout_s = self.timeout
			
		if (ser.isOpen() == False):
			ser.open()

		self.compose = ""
		self.compose = str(command) + "\r"
		# debug_print(self.compose)
		ser.write(self.compose.encode())
		
		self.response =""
		ser.reset_input_buffer()
		start_time = time.time()
		while(time.time() - start_time < timeout_s):
			try:
				if(ser.in_waiting > 0):
					self.response += ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
				delay(100)
			except Exception as e:
				debug_print(e.Message)
			# debug_print(self.response)
					
			if(self.response.find(desired_response) != -1):
				debug_print(self.response)
				return True

		debug_print("TIMEOUT after " + str(timeout_s) + " sec in AT command: " + self.compose + "\r\n")
		return False

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
		self.sendATcmd("AT+QGPS?")
		self.sendATcmd("AT+QGPS=1")
		self.sendATcmd("AT+QGPS?")

	def gnssOff(self):
		self.sendATcmd("AT+QGPSEND")
		self.sendATcmd("AT+QGPS?")

	def updateGnssLocation(self):
		if(self.sendATcmd("AT+QGPSLOC?", "OK\r\n", 2.)):
			#self.response = "+QGPSLOC: 072121.0,51.23878,6.72306,1.2,54.3,2,0.00,0.0,0.0,080620,12\r\n"
			#self.response = "+QGPSLOC: 121445.0,51.23871,6.72304,1.0,53.8,3,0.00,0.0,0.0,050620,12\r\n"
			fields = list(csv.reader([self.response[10:]]))[0]
			self.latitude = fields[1]
			self.longitude = fields[2]
		else:
			print (self.response)
			self.latitude = .0
			self.longitude = .0
		return [self.latitude, self.longitude]

	def getSatellitesInfo(self):
		self.sendATcmd('AT+QGPSGNMEA="GSV"')



if __name__=='__main__':

	import serial.tools.list_ports
	ports = list(serial.tools.list_ports.comports())
	for p in ports:
		print(p)

	module = BG770A()	#(serial_port="/dev/ttyS0", serial_baudrate=9600, board="Sixfab NB-IoT Shield")

	module.sendATcmd("AT","OK")
	module.gnssOn();
	module.updateGnssLocation();
