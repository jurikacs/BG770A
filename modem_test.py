'''
  modem_test - This is basic This is basic Finamon GNSS/Modem BG770A modem using example.
'''

import BG770A
import time

remote_ip = "xx.xx.xx.xx"   # change with your remote ip
remote_port = "xxxx"        # change with your remote port

modem = BG770A.BG770A(serial_port="/dev/ttyS0", serial_baudrate=9600, board="Sixfab NB-IoT Shield")

modem.sendATcmd("ATE1","OK\r\n")

modem.getIMEI()
time.sleep(0.5)
modem.getFirmwareInfo()
time.sleep(0.5)
modem.getHardwareInfo()
time.sleep(0.5)

modem.setIPAddress(remote_ip)
time.sleep(0.5)
modem.setPort(remote_port)
time.sleep(0.5)

modem.connectToOperator()
time.sleep(0.5)

modem.closeConnection()
time.sleep(0.5)
modem.startUDPService()
time.sleep(0.5)

modem.sendDataUDP("Hello World!\r\n")
time.sleep(0.5)

