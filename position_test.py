'''
  position_test.py - This is basic Finamon GNSS/Modem BG770A positioning function example.
'''
import BG770A
import time

print("GPS-4G_HAT shield. Show position demo")
print("module on at " + time.strftime("%H:%M:%S"))
navigator = BG770A.BG770A()

navigator.gnssOn()
print("gps start at " + time.strftime("%H:%M:%S"))
while(True):
    time.sleep(2.)
    
    navigator.acquirePositionInfo()
    print("position latitude: " + str(navigator.latitude) +  ", longitude: " + str(navigator.longitude))
    
    navigator.getSatellitesInfo()
    time.sleep(.5)

    navigator.sendATcmd('AT+QGPSGNMEA="GGA"')
    time.sleep(.5)
    navigator.sendATcmd('AT+QGPSGNMEA="RMC"')
    time.sleep(.5)
    navigator.sendATcmd('AT+QGPSGNMEA="GSA"')
    time.sleep(.5)
    navigator.sendATcmd('AT+QGPSGNMEA="VTG"')

navigator.gnssOff()

'''
AT+QGPSLOC?
+QGPSLOC: 110434.000,5113.7522N,642.8649E,9.3,0.0,2,161.60,0.0,0.0,170622,3

OK
'''

