import binascii
import socket
import sys

import re

from enum import Enum

#51.22905639120505, 6.714667813472686
#51.22906, 6.71467

# https://www.debuggex.com/
#regex = re.compile(r'.+\s+SEND OK\s+\+QIURC: "recv",\d+,(\d+)\s+(.+)')
#regex = re.compile(r'.+\s+\+QGPSLOC: \d+\.\d+,(\d+\.\d+)\w,(\d+\.\d+)\w.+')
regex = re.compile(r'AT\+GSN\s+(\d+)')

#test = "+QIURC: \"recv\",0,13\r\nHello Finamon"
#test = 'Hello Finamon\r\nSEND OK\r\n\r\n+QIURC: "recv",0,13\r\nHello Finamon'
#test = "AT+QGPSLOC\r\n\r\n+QGPSLOC: 131604.000,5113.7451N,642.8864E,2.6,0.0,3,69.00,0.0,0.0,170622,4\r\n\r\nOK\r\n"
test = "AT+GSN\r\n\r\n866349041749536\r\n\r\nOK\r\n"

res = regex.match(test)
if res:
    print(res.group(1))  #, res.group(2))
else:
    print("no match")
sys.exit(0)



# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#server_address = ('52.215.34.155', 7)   #"echo.mbedcloudtesting.com"
server_address = ('echo.mbedcloudtesting.com', 7)   #"echo.mbedcloudtesting.com"

message = 'This is the message. It will be repeated.'

try:

    # Send data
    print ('sending "%s"' % message)
    sent = sock.sendto(message.encode(), server_address)

    # Receive response
    print ('waiting to receive')
    data, server = sock.recvfrom(1024)
    print ('received "%s"' % data)
    print ('received "%s"' % binascii.hexlify(data))

finally:
    print ('closing socket')
    sock.close()
