'''
  position_test.py - This is basic Finamon GNSS/Modem BG770A positioning function example.
'''

import BG770A
import time


navigator = BG770A.BG770A(serial_port="/dev/ttyS0", serial_baudrate=9600, board="Sixfab NB-IoT Shield")

navigator.gnssOn()

navigator.updateGnssLocation()
navigator.getSatellitesInfo()

navigator.gnssOff()
