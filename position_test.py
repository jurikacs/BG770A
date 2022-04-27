'''
  position_test.py - This is basic Finamon GNSS/Modem BG770A positioning function example.
'''

import BG770A
import time


navigator = BG770A.BG770A()

navigator.gnssOn()

navigator.updateGnssLocation()
print("position latitude: " + str(navigator.latitude) +  ", longitude: " + str(navigator.longitude))

navigator.getSatellitesInfo()

navigator.sendATcmd('AT+QGPSGNMEA="GGA"')
navigator.sendATcmd('AT+QGPSGNMEA="RMC"')
navigator.sendATcmd('AT+QGPSGNMEA="GSA"')
navigator.sendATcmd('AT+QGPSGNMEA="VTG"')

navigator.gnssOff()
