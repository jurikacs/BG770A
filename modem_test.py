'''
  modem_test - This is basic This is basic Finamon GNSS/Modem BG770A modem using example.
'''

import sys
from BG770A import BG770A

remote_ip = "89.107.68.161" # change with your remote ip
remote_port = 9098          # change with your remote port

if "win" not in sys.platform: 
	ser_port = "/dev/serial0"
else: 
	ser_port = "COM4"

modem = BG770A(serial_port = ser_port)

#modem.sendATcmd("ATE1","OK\r\n")
#modem.sendATcmd("AT+CMEE=2")

#modem.getIMEI()
#modem.getFirmwareInfo()
#modem.getHardwareInfo()

#modem.sendATcmd("AT+CPIN?")

#contextID = 1
#modem.setIPAddress(remote_ip)
#modem.setPort(remote_port)

#modem.initNetwork();
#modem.configTcpIpContext(contextID, "web.vodafone.de")
#modem.activatePdpContext(contextID, 5)

#modem.openConnection(contextID, "UDP", 5)
#modem.sendUdpData("Hello Finamon")

#modem.closeConnection()
#modem.deactivatePdpContext(contextID, 5)

scen_ping = [
	["at",			"OK\r\n",	1.],
	["at+cmee=2",	"OK\r\n",	1.],
	["at+cpin?",	"OK\r\n",	1.],
	["at+cfun=1",	"OK\r\n",	1.],
	["at+cops?",	"OK\r\n",	3.],
	["at+qicsgp=1,1,\"web.vodafone.de\",\"\",\"\",1",	"OK\r\n",	1.],
	["at+qiact=1",	"OK\r\n",	1.],
	["at+qiact?",	"OK\r\n",	1.],
	["at+creg=2",	"OK\r\n",	1.],
	["at+creg?",	"OK\r\n",	1.],
	["at+qping=1,\"89.107.68.161\"",	"OK\r\n",	1.],
	]

scen_echo = [
	["at",			"OK\r\n",	1.],
	["at+cmee=2",	"OK\r\n",	1.],
	["at+cpin?",	"OK\r\n",	1.],
	["at+cfun=1",	"OK\r\n",	1.],
	["at+cops?",	"OK\r\n",	3.],
	["at+qicsgp=1,1,\"web.vodafone.de\",\"\",\"\",1",	"OK\r\n",	1.],
	["at+qiact=1",	"OK\r\n",	1.],
	["at+qiact?",	"OK\r\n",	1.],
	["at+creg=2",	"OK\r\n",	1.],
	["at+creg?",	"OK\r\n",	1.],
	["at+qping=1,\"89.107.68.161\"",	"OK\r\n",	1.],
	]

modem.runScenario(scen_ping)
modem.getResponse(5.)
