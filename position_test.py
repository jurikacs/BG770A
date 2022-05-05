'''
  position_test.py - This is basic Finamon GNSS/Modem BG770A positioning function example.
'''

import BG770A
import pprint
import time


navigator = BG770A.BG770A()

navigator.gnssOn()

sleep_time = 10
start_time = time.time()
while(not navigator.acquirePositionInfo()):
    navigator.sendATcmd('AT+QGPSGNMEA="GSV"')
    time.sleep(sleep_time)

print ("position search time %s seconds" % int(time.time() - start_time))

for i in range(50):
    navigator.acquireNmeaSentence("GGA")
    navigator.acquireNmeaSentence("GSA")
    navigator.acquireNmeaSentence("RMC")
    navigator.acquireNmeaSentence("VTG")

    sat_info = navigator.acquireSatellitesInfo()
    #pprint.pprint(repr(sat_info))

    location_dict = navigator.acquirePositionInfo()
    #pprint.pprint(location_dict)
    time.sleep(2.)

navigator.gnssOff()

#test data
#line = '114646.000,5113.7365N,642.9073E,5.7,0.0,3,150.30,0.0,0.0,040522,4'
#self.response = 'AT+QGPSGNMEA="GSV"\r\r\n+QGPSGNMEA: $GPGSV,3,1,11,05,09,029,14,07,05,337,,08,05,277,,10,15,158,*7A\r\n+QGPSGNMEA: $GPGSV,3,2,11,16,69,275,,18,58,065,33,23,33,131,34,26,60,186,*7F\r\n+QGPSGNMEA: $GPGSV,3,3,11,27,40,280,,29,15,088,26,31,02,197,,,,,*46\r\n+QGPSGNMEA: $GLGSV,2,1,08,65,03,354,,66,21,047,25,67,12,099,11,73,58,281,*6B\r\n+QGPSGNMEA: $GLGSV,2,2,08,80,41,196,,81,09,058,14,82,55,040,27,84,08,246,*69\r\n\r\nOK\r\n'

