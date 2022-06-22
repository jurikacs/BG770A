'''
	Finamon BG770A Library 
	Library for Finamon GNSS/Modem BG770A Shield.
'''

import csv
import pynmea2
import re
import serial
import sys
import time
import pprint

bRPi = False
if "win" not in sys.platform: 
	import RPi.GPIO as GPIO
	bRPi = True

# Peripheral Pin Definations
RESET = 19
PWRKEY = 26

# global variables
TIMEOUT = 1.0 # seconds
ser = serial.Serial()

#----------------------------------------
#	Private Methods#
#----------------------------------------

# function for getting time as miliseconds
def millis():
	return int(time.time()*1000)

# function for delay as miliseconds
def delay(ms):
	#debug_print("sleep, s " + str(ms/1000.0)) 
	time.sleep(float(ms/1000.0))

#----------------------------------------
#	GNSS/Modem BG770A Shield Class
#----------------------------------------
class BG770A:
	board = ""			# Shield name
	IMEI = "not defined"
	ip_address = ""
	domain_name = ""
	port_number = ""
	timeout = TIMEOUT	# default timeout
	connectID = '0'		# defuault connect ID
	
	compose = ""
	response = ""

	latitude = 0
	longitude = 0
	
	mgtt_client_idx = "0"

	multiline = False
	
	# Default Initializer
	def __init__(self, serial_port="/dev/serial0", serial_baudrate=115200, board="Finamon GNSS/Modem BG770A Shield"):
		
		self.board = board
	
		ser.port = serial_port
		if "win" in sys.platform:
			ser.port = "COM4"

		ser.baudrate = serial_baudrate
		ser.parity=serial.PARITY_NONE
		ser.stopbits=serial.STOPBITS_ONE
		ser.bytesize=serial.EIGHTBITS

		self.debug_print(self.board + " created")

		if not bRPi:
			return

		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		
		GPIO.setup(RESET,GPIO.OUT)
		GPIO.output(RESET,GPIO.HIGH)
		delay(1000)
		GPIO.output(RESET,GPIO.LOW)
		delay(500)

		GPIO.setup(PWRKEY,GPIO.OUT)
		GPIO.output(PWRKEY,GPIO.HIGH)
		delay(1000)
		GPIO.output(PWRKEY,GPIO.LOW)
		
		ser.open()
		self.waitUnsolicited("APP RDY", 20)
		#delay(3000)
		
	def close(self):
		ser.close()

	# Function for getting modem response
	def getResponse(self, timeout_s = None):
		if timeout_s is None:
			timeout_s = self.timeout
		if (ser.isOpen() == False):
			ser.open()
		
		self.response =""
		start_time = time.time()
		while(time.time() - start_time < timeout_s):	
			if(ser.in_waiting):
				self.response += ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
		if(self.response):
			self.debug_print(self.response)

	# Function for getting modem response
	def waitUnsolicited(self, desired_response = "", timeout_s = None):
		if timeout_s is None:
			timeout_s = self.timeout
		if (ser.isOpen() == False):
			ser.open()
		
		self.response =""
		start_time = time.time()
		while(time.time() - start_time < timeout_s):	
			if(ser.in_waiting):
				self.response += ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
			if(self.response.find(desired_response) != -1):
				self.debug_print(self.response)
				return True
		if(self.response):
			self.debug_print("UNEXPECTED responce: " + self.response + " after " + str(timeout_s) + " sec, awaiting: " + desired_response + "\r\n")
		else:
			self.debug_print("TIMEOUT after " + str(timeout_s) + " sec, awaiting: " + desired_response + "\r\n")
		return False

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
				self.debug_print(e.Message)
					
			if(self.response.find(desired_response) != -1):
				self.debug_print(self.response)
				return True

			if(self.response.find("ERROR") != -1):
				self.debug_print(self.response)
				return False

		self.debug_print("TIMEOUT after " + str(timeout_s) + " sec, AT command: " + self.compose + "\r\n")
		return False

	# Function for saving conf. and reset BG770A module
	def resetModule(self):
		self.saveConfigurations()
		delay(200)
		#TODO HW reset

	# Function for save configurations shield be done in current session. 
	def saveConfigurations(self):
		self.sendATcmd("AT&W","OK\r\n")

	# Function for getting IMEI number
	def getIMEI(self):
		self.sendATcmd("AT+GSN","OK\r\n")
		regex = re.compile(r'AT\+GSN\s+(\d+)')
		result = regex.match(self.response)
		if result:
			self.IMEI = result.group(1)

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
		#self.sendATcmd("AT+CFUN=1", "OK\r\n", 2)
		self.sendATcmd("AT+COPS?", "OK\r\n", 2)

	# Function for cheking network registration
	def checkRegistration(self):
		self.sendATcmd("AT+CEREG=0")
		self.sendATcmd("AT+CEREG?", "+CEREG: 0,5", 120)

	# Function for getting signal quality
	def getSignalQuality(self):
		self.sendATcmd("AT+CSQ","OK\r\n", 5)
		return self.sendATcmd("AT+QCSQ","OK\r\n", 5)


	#----------------------------------------------------------------------------------------
	#	Connection Functions
	#----------------------------------------------------------------------------------------

	# Function for configuring parameters of a TCP/IP context
	def configTcpIpContext(self, contextID, APN, username = "", password = "", timeout_s = None):
		self.compose = "AT+QICSGP=" + contextID + ",1,\""
		self.compose += str(APN) + "\",\""
		self.compose += str(username) + "\",\""
		self.compose += str(password) + "\",1"
		return self.sendATcmd(self.compose, "OK\r\n", timeout_s)

	# Function for PDP context activation
	def activatePdpContext(self, contextID, timeout_s = 150):
		ret = self.sendATcmd("AT+QIACT=" + contextID, "OK\r\n", timeout_s)
		self.sendATcmd("AT+QIACT?", "OK\r\n", 10)
		return ret

	# Function for PDP context deactivation
	def deactivatePdpContext(self, contextID, timeout_s = 40):
		return self.sendATcmd("AT+QIDEACT=" + contextID, "OK\r\n", timeout_s)

	# Function for opening server connection
	def openConnection(self, contextID, service_type = "UDP", timeout_s = 150):
		self.compose = "AT+QIOPEN=" + contextID + "," + self.connectID + ",\""
		self.compose += str(service_type) + "\",\""
		self.compose += str(self.ip_address) + "\","
		self.compose += str(self.port_number) + ",0,0"
		return self.sendATcmd(self.compose, "+QIOPEN: 0,", timeout_s)

	# Function for closing server connection
	def closeConnection(self):
		self.sendATcmd("AT+QICLOSE=" + self.connectID)

	def runScenario(self, list_AT_cmd):
		ret = True
		for cmd in  list_AT_cmd:
			ret &= self.sendATcmd(cmd[0], cmd[1], cmd[2])
			delay(2500)
		return ret

	#----------------------------------------------------------------------------------------
	#	UDP Protocols Functions
	#----------------------------------------------------------------------------------------
	
	# Function for sending data via udp.
	def sendUdpData(self, data):
		self.compose = "AT+QISEND=" + self.connectID + "," + str(len(data))
		if self.sendATcmd(self.compose,">"):
			ser.write(data.encode())
			self.waitUnsolicited("SEND OK", 5)
		else:
			self.debug_print("ERROR message not send \"" + str(data.encode()) + "\"\r\n")

	# Function for receiving  data via udp.
	def recvUdpData(self):
		ret = ""
		if(self.waitUnsolicited("+QIURC: \"recv\"," + self.connectID), 5):
			regex = re.compile(r'.+\s+SEND OK\s+\+QIURC: "recv",\d+,(\d+)\s+(.+)')
			result = regex.match(self.response)
			if result:
				ret = result.group(2)
			self.sendATcmd("AT+QIRD=" + self.connectID)
		return ret

	#----------------------------------------------------------------------------------------
	#	GNSS Functions
	#----------------------------------------------------------------------------------------

	def gnssOn(self):
		self.sendATcmd("AT+QGPS?")
		self.sendATcmd("AT+QGPS=1")
		delay(1000)
		if self.sendATcmd("AT+QGPS?", "+QGPS:1"):
			return True
		else:
			return False

	def gnssOff(self):
		self.sendATcmd("AT+QGPSEND")
		self.sendATcmd("AT+QGPS?")

	def acquireGnssSettings(self):
		settings = [
			"outport",
			"gnssconfig",
			"nmeafmt",
			"gpsnmeatype",
			"glonassnmeatype",
			"nmeasrc",
			"autogps",
			"priority",
			"xtrafilesize",
			"xtra_info",
			"gpsdop",
			"estimation_error",
			"xtra_download",
			"test_mode",
		]
		self.sendATcmd('AT+QGPSCFG=?')
		for setting in settings:
			self.sendATcmd('AT+QGPSCFG="' + setting + '"')

	def acquirePositionInfo(self):
		self.sendATcmd('AT+QGPSLOC?')
		if(self.response.find('ERROR') != -1):
			return False
		start = len('AT+QGPSLOC?\r\r\n+QGPSLOC: ')
		end = self.response.find('\r', start)
		line = self.response[start : end]
		if not line:
			return False
		#debug_print(line)
		fields = list(csv.reader([line]))[0]
		gpsloc = {}
		parameters = ['utc','latitude','longitude','hdop','altitude','fix','cog','spkm','spkn','date','nsat']
		for i, param in enumerate(parameters):
			gpsloc[param] = fields[i]
		return gpsloc

	def acquireSatellitesInfo(self):
		self.sendATcmd('AT+QGPSGNMEA="GSV"')
		start = len('AT+QGPSGNMEA="GSV"\r\r\n')
		sat_info = []
		while (True):
			start = self.response.find('$G', start + 6)
			end = self.response.find('*', start) + 3
			if (start < 0):
				break
			line = self.response[start : end]
			if self.writeGnssFile:
				#debug_print(line)
				self.log_file.write(line + '\n')
			msg = pynmea2.parse(line)
			sat_info.append(msg)
		return sat_info

	def acquireNmeaSentence(self, sentence = 'GGA'):
		self.response =''
		self.sendATcmd('AT+QGPSGNMEA="' + sentence + '"')
		start = self.response.find('+QGPSGNMEA: ') 
		if (start < 0):
			return	
		start += len('+QGPSGNMEA: ')
		end = self.response.find('*', start) + 3
		if (end < 0):
			return	
		line = self.response[start : end]
		if self.writeGnssFile:
			#debug_print(line)
			self.log_file.write(line + '\n')
		msg = pynmea2.parse(line)
		self.debug_print(repr(msg))


	#----------------------------------------------------------------------------------------
	#	Geofences Functions
	#----------------------------------------------------------------------------------------
	#+QCFGEXT: "addgeo",<geoid>,<mode>,<shape>,<lat1>,<lon1>,<lat2>,[<lon2>,[<lat3>,<lon3>[,<lat4>,<lon4>]]]

	#	<geoid> Integer type. Geo-fence ID. Range: 09.
	#	<mode> Integer type. URC report mode.
	#		0 Disable URC to be reported when entering or leaving the geo-fence
	#		1 Enable URC to be reported when entering the geo-fence
	#		2 Enable URC to be reported when leaving the geo-fence
	#		3 Enable URC to be reported when entering or leaving the geo-fence
	#	<shape> Integer type. Geo-fence shape.
	#		0 Circularity with center and radius
	#		1 Circularity with center and one point on the circle
	#		2 Triangle
	#		3 Quadrangle

	def addGeofence(self, geoid, mode, shape, geofence, radius = 0):
		coord_string = ''
		for i, position in enumerate(geofence):
			coord_string += ',' + str(position[0]) + ',' + str(position[1])
		if radius:
			coord_string += ',' + str(radius)
		self.sendATcmd('AT+QCFGEXT="addgeo",%d,%d,%d%s' % (int(geoid), int(mode), int(shape), coord_string))

	def deleteGeofence(self, geoid):
		self.sendATcmd('AT+QCFGEXT="deletegeo",' + str(geoid))

	# return value: position with respect to geo-fence.
	#	0 Position unknown
	#	1 Position is inside the geo-fence
	#	2 Position is outside the geo-fence
	#	3 Geo-fence ID does not exist
	def queryGeofence(self, geoid):
		cmd_string = '"querygeo",' + str(geoid)
		self.sendATcmd('AT+QCFGEXT=' + cmd_string)
		if(self.response.find("+CME ERROR:") == -1):
			pos = self.response.find(cmd_string+',')
			return int(self.response[pos + len(cmd_string) + 1])
		else:
			return 3

	#----------------------------------------------------------------------------------------
	#	IoT Functions
	#----------------------------------------------------------------------------------------

	def acquireMqttSettings(self, client_idx = "0"):
		settings = [
			"aliauth",
			"keepalive",
			"pdpcid",
			"recv/mode",
			"session",
			"ssl",
			"timeout",
			"version",
			"will"]
		self.sendATcmd('AT+QMTCFG=?')
		for setting in settings:
			self.sendATcmd('AT+QMTCFG="' + setting + '",' + client_idx)

	def openMqttConnection(self, client_idx = "0", host_name = "", port = 1883):
		self.mgtt_client_idx = client_idx
		self.sendATcmd('AT+QMTOPEN='+ self.mgtt_client_idx +',"' + host_name + '",' + str(port))
		self.waitUnsolicited( "+QMTOPEN:", 5)
		self.sendATcmd('AT+QMTOPEN?')

	def connectMqttClient(self, client_id_string, username, password):
		self.sendATcmd('AT+QMTCONN='+ self.mgtt_client_idx +',"' + client_id_string + '","' + username + '","' + password+ '"')
		self.waitUnsolicited( "+QMTCONN:", 5)

	def publishMqttMessage(self, topic, message):
		self.compose = 'AT+QMTPUB='+ self.mgtt_client_idx +',1,1,0,"' + topic + '",' + str(len(message))
		if self.sendATcmd(self.compose,">"):
			ser.write(message.encode())
			self.waitUnsolicited("+QMTPUB:", 5)
		else:
			self.debug_print("ERROR mqqt message \"" + str(message.encode()) + "\" not publish\r\n")

	def subscribeToMqttTopic(self, topic):
		self.sendATcmd('AT+QMTSUB='+ self.mgtt_client_idx +',1,"' + topic + '",2')
		self.waitUnsolicited("+QMTSUB:", 5)

	def unsubscribeFromMqttTopic(self, topic):
		self.sendATcmd('AT+QMTUNS='+ self.mgtt_client_idx +',1,"' + topic + '"')
		self.waitUnsolicited("+QMTUNS:", 5)


	#----------------------------------------------------------------------------------------
	#	Debug Functions
	#----------------------------------------------------------------------------------------

	# function for printing debug message 
	def debug_print(self, message):
		if not self.multiline:
			message = message.replace("\r", ".") 
			message = message.replace("\n", ".")
		print('[' + time.strftime("%H:%M:%S") + '] ' + message)	



if __name__=='__main__':

	import serial.tools.list_ports
	ports = list(serial.tools.list_ports.comports())
	for p in ports:
		print(p)

	if "win" not in sys.platform: 
		ser_port = "/dev/serial0"
	else: 
		ser_port = "COM4"

	module = BG770A(serial_port = ser_port)
	delay(2000)
	module.sendATcmd("AT")
	module.getHardwareInfo()
	module.getFirmwareInfo()
	module.getIMEI()

	module.sendATcmd("AT+CMEE=2")
	module.sendATcmd("AT+CPIN?", "OK\r\n", 5)
	#module.sendATcmd("AT+CPIN=\"1234\"", "OK\r\n", 5)
	module.sendATcmd("AT+CFUN?")
	module.sendATcmd("AT+CREG=0", "OK\r\n", 10)
	#module.sendATcmd("AT+COPS=?", "OK\r\n", 600)
	while not module.sendATcmd("AT+CREG?", "+CREG: 0,5", 10):
		delay(10*1000)

	module.getSignalQuality()
	module.checkRegistration()
	module.sendATcmd("AT+QNWINFO", "OK\r\n", 10)

	contextID = "1"
	module.setIPAddress("52.215.34.155")	# "89.107.68.161"
	module.setPort(7)						# 9098

	module.configTcpIpContext(contextID, "wsim")
	module.activatePdpContext(contextID, 5)

	module.openConnection(contextID, "UDP", 5)
	module.sendUdpData("Hello " + module.board + " IMEI: " + module.IMEI)
	module.recvUdpData()

	module.closeConnection()
	module.deactivatePdpContext(contextID, 5)
	#module.gnssOn();
	#module.updateGnssLocation();
	module.close()
	
#AT+COPS=? +COPS:
#	(1,"Vodafone.de","Vodafone","26202",9),
#	(1,"Telekom.de","TDG","26201",8),
#	(1,"o2 - de","o2 - de","26203",8),
#	(1,"Vodafone.de","Vodafone","26202",8),
#	,(0,1,2,3,4),(0,1,2)

