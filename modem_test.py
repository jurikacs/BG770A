'''
  modem_test - This is basic This is basic Finamon GNSS/Modem BG770A modem using example.
'''

import BG770A
import time

remote_ip = "89.107.68.161" # change with your remote ip
remote_port = 9098          # change with your remote port

modem = BG770A.BG770A()

modem.sendATcmd("ATE1","OK\r\n")
modem.sendATcmd("AT+CMEE=2")

modem.getIMEI()
modem.getFirmwareInfo()
modem.getHardwareInfo()

modem.sendATcmd("AT+CPIN?")

contextID = 1
modem.setIPAddress(remote_ip)
modem.setPort(remote_port)

modem.initNetwork();
modem.configTcpIpContext(contextID, "1and1")
modem.activatePdpContext(contextID, 5)

modem.openConnection(contextID, "UDP", 5)
modem.sendUdpData("Hello Finamon")

modem.closeConnection()
modem.deactivatePdpContext(contextID, 5)

