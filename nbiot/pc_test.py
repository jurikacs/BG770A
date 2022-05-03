import binascii
import socket
import sys

import re


regex = re.compile(r'.+\s+SEND OK\s+\+QIURC: "recv",\d+,(\d+)\s+(.+)')
#test = "+QIURC: \"recv\",0,13\r\nHello Finamon"
test = 'Hello Finamon\r\nSEND OK\r\n\r\n+QIURC: "recv",0,13\r\nHello Finamon'

res = regex.match(test)
print(res.group(1), res.group(2))



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
