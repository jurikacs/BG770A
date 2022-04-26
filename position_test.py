'''
  position_test.py - This is basic Finamon GNSS/Modem BG770A positioning function example.
'''

import BG770A
import time


navigator = BG770A.BG770A()

navigator.gnssOn()

navigator.updateGnssLocation()
navigator.getSatellitesInfo()

navigator.gnssOff()
