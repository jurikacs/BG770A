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

#----------------------------------------
#	Private Methods#
#----------------------------------------

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

#----------------------------------------
#	GNSS/Modem BG770A Shield Class
#----------------------------------------
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
		
	# Function for getting modem response
	def getResponse(self, desired_response):
		if (ser.isOpen() == False):
			ser.open()
			
		while 1:	
			self.response =""
			while(ser.in_waiting):
				self.response += ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
			if(self.response.find(desired_response) != -1):
				debug_print(self.response)
				break

	# Function for sending at command to BG770A.
	def sendATcmd(self, command, desired_response = "OK\r\n", timeout_s = None):
		
		if timeout_s is None:
			timeout_s = self.timeout
			
		if (ser.isOpen() == False):
			ser.open()

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

			if(self.response.find("ERROR") != -1):
				debug_print(self.response)
				return False

		debug_print("TIMEOUT after " + str(timeout_s) + " sec, AT command: " + self.compose + "\r\n")
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


	#----------------------------------------------------------------------------------------
	#	Network Service Functions
	#----------------------------------------------------------------------------------------

	# Function for setting common mobile network parameters
	def initNetwork(self):
		self.sendATcmd("AT+CFUN=1", "OK\r\n", 2)
		self.sendATcmd("AT+COPS?", "OK\r\n", 2)

	# Function for cheking network registration
	def checkRegistration(self):
		self.sendATcmd("AT+CREG=2")
		self.sendATcmd("AT+CEREG?")

	# Function for getting signal quality
	def getSignalQuality(self):
		return self.sendATcmd("AT+CSQ","OK\r\n")


	#----------------------------------------------------------------------------------------
	#	Connection Functions
	#----------------------------------------------------------------------------------------

	# Function for configuring parameters of a TCP/IP context
	def configTcpIpContext(self, contextID, APN, username = "", password = "", timeout_s = None):
		self.compose = "AT+QICSGP=" + str(contextID) + ",1,\""
		self.compose += str(APN) + "\",\""
		self.compose += str(username) + "\",\""
		self.compose += str(password) + "\",1"
		return self.sendATcmd(self.compose, "OK\r\n", timeout_s)

	# Function for PDP context activation
	def activatePdpContext(self, contextID, timeout_s = 150):
		ret = self.sendATcmd("AT+QIACT=" + str(contextID), "OK\r\n", timeout_s)
		self.sendATcmd("AT+QIACT?", "OK\r\n", 10)
		return ret

	# Function for PDP context deactivation
	def deactivatePdpContext(self, contextID, timeout_s = 40):
		return self.sendATcmd("AT+QIDEACT=" + str(contextID), "OK\r\n", timeout_s)

	# Function for opening server connection
	def openConnection(self, contextID, service_type = "UDP", timeout_s = 150):
		self.compose = "AT+QIOPEN=" + str(contextID) + ",0,\""
		self.compose += str(service_type) + "\",\""
		self.compose += str(self.ip_address) + "\","
		self.compose += str(self.port_number) + ",0,1"
		return self.sendATcmd(self.compose, "+QIOPEN: 0,", timeout_s)

	# Function for closing server connection
	def closeConnection(self):
		self.sendATcmd("AT+QICLOSE=0")

	#----------------------------------------------------------------------------------------
	#	UDP Protocols Functions
	#----------------------------------------------------------------------------------------
	
	# Function for sending data via udp.
	def sendUdpData(self, data):
		self.compose = "AT+QISEND=0," + str(len(data))
		if self.sendATcmd(self.compose,">"):
			ser.write(data.encode())
		else:
			debug_print("ERROR message: \"" + str(data.encode()) + "\" not send\r\n")

	#----------------------------------------------------------------------------------------
	#	GNSS Functions
	#----------------------------------------------------------------------------------------

	def gnssOn(self):
		self.sendATcmd("AT+QGPS?")
		self.sendATcmd("AT+QGPS=1")
		self.sendATcmd("AT+QGPS?")

	def gnssOff(self):
		self.sendATcmd("AT+QGPSEND")
		self.sendATcmd("AT+QGPS?")

	def updateGnssLocation(self):
		if(self.sendATcmd("AT+QGPSLOC?", "OK\r\n", 2.)):
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

	module = BG770A()	#(serial_port="/dev/ttyUSB0", serial_baudrate=9600, board="Sixfab NB-IoT Shield")

	module.sendATcmd("AT")
	module.sendATcmd("AT+CMEE=2")
	module.sendATcmd("AT+CPIN?", "OK\r\n", 5)
	module.sendATcmd("AT+CPIN=\"7161\"", "OK\r\n", 5)

	contextID = 1
	module.setIPAddress("89.107.68.161")
	module.setPort(9098)

	module.initNetwork();
	module.configTcpIpContext(contextID, "web.vodafone.de")
	module.activatePdpContext(contextID, 5)

	module.openConnection(contextID, "UDP", 5)
	module.sendUdpData("Hello Finamon")

	module.closeConnection()
	module.deactivatePdpContext(contextID, 5)

	#module.gnssOn();
	#module.updateGnssLocation();
