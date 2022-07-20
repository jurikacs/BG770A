'''
  demo_GPS_4G_HAT.py - This is Finamon GPS-4G-HAT shield funktionality demo
'''

#from asyncio.windows_events import NULL
from BG770A import BG770A
from datetime import datetime
import time

import json


#----------------------------------------------------------------------------------------
#	JSON stuff
#----------------------------------------------------------------------------------------

mqtt_json_string = """
{
"shield":
    {
        "imei": 0,
        "ip":   "127.0.0.1",
        "inp":  0,
        "out":  0,
        "led":  1,
        "but":  0
    }
,
"pos": [
    {
        "lat": 0,
        "lon": 0,
        "utc": 0
    }
],
"acc": [
    {
        "x":    0,
        "y":    0,
        "z":    0,
        "stat": 0,
        "utc":  0
    }
]
}
"""

gps_json_string = """{
    "imei": 0,
    "latitude": 0,
    "longitude": 0,
    "altitude": 0,
    "utc": 0
}"""

def nmea2json (gpsloc):

    mqtt_json = json.loads(mqtt_json_string)

    mqtt_json["shield"]['imei'] = int(module.IMEI)

    point = gpsloc['latitude'].find('.')
    gradus = float(gpsloc['latitude'][0:point-2])
    minute = float(gpsloc['latitude'][point-2:-1])/60
    mqtt_json["pos"][0]['lat'] = round(gradus + minute, 6)
    if gpsloc['latitude'][-1] == 'S':
        mqtt_json["pos"][0]['lat'] = - mqtt_json["pos"][0]['lat']

    point = gpsloc['longitude'].find('.')
    gradus = float(gpsloc['longitude'][0:point-2])
    minute = float(gpsloc['longitude'][point-2:-1])/60
    mqtt_json["pos"][0]['lon'] = round(gradus + minute, 6)
    if gpsloc['longitude'][-1] == 'W':
        mqtt_json["pos"][0]['lon'] = - mqtt_json["pos"][0]['lon']

    dt = datetime(
        2000 + int(gpsloc['date'][4:]), # year
        int(gpsloc['date'][2:4]),
        int(gpsloc['date'][0:2]),
        int(gpsloc['utc'][0:2]),        # hour
        int(gpsloc['utc'][2:4]),
        int(gpsloc['utc'][4:6]),
        )
    mqtt_json["pos"][0]['utc'] = dt.timestamp()

    mqtt_json["acc"][0]['utc'] = round(datetime.utcnow().timestamp(), 1)  #TODO move to accel stuff

    return mqtt_json


def nmea2gps_json (gpsloc):

    mqtt_json = json.loads(gps_json_string)

    mqtt_json['imei'] = int(module.IMEI)

    point = gpsloc['latitude'].find('.')
    gradus = float(gpsloc['latitude'][0:point-2])
    minute = float(gpsloc['latitude'][point-2:-1])/60
    mqtt_json['latitude'] = round(gradus + minute, 6)
    if gpsloc['latitude'][-1] == 'S':
        mqtt_json['latitude'] = - mqtt_json['latitude']

    point = gpsloc['longitude'].find('.')
    gradus = float(gpsloc['longitude'][0:point-2])
    minute = float(gpsloc['longitude'][point-2:-1])/60
    mqtt_json['longitude'] = round(gradus + minute, 6)
    if gpsloc['longitude'][-1] == 'W':
        mqtt_json['longitude'] = - mqtt_json['longitude']

    mqtt_json['altitude'] = gpsloc['altitude']

    dt = datetime(
        2000 + 
        int(gpsloc['date'][4:]),    # year
        int(gpsloc['date'][2:4]),
        int(gpsloc['date'][0:2]),
        int(gpsloc['utc'][0:2]),    # hour
        int(gpsloc['utc'][2:4]),
        int(gpsloc['utc'][4:6]),
        )
    mqtt_json['utc'] = dt.timestamp()
    return mqtt_json

#----------------------------------------------------------------------------------------
#	MQTT service data
#----------------------------------------------------------------------------------------

#mqtt_broker = 'broker.emqx.io'
#mqtt_port = 1883
#mqtt_topic = "qf4dcfae.eu-central-1.emqx.cloud"
## generate client ID with pub prefix randomly
#mqtt_client_id_string = ""
#mqtt_username = 'finamon'
#mqtt_password = 'Finamon_2022'
#mqtt_msg = ''

mqtt_broker = '23.88.108.59'
mqtt_port = 1883
mqtt_client_id = 'TBD'
mqtt_username = 'api'
mqtt_password = 'flake-iraq-contra'
mqtt_topic = "gps/coordinates"

#----------------------------------------------------------------------------------------
#	init GPS/communication module BG77x and data structures
#----------------------------------------------------------------------------------------

module = BG770A()

module.sendATcmd("AT")
module.getHardwareInfo()
module.getFirmwareInfo()
module.getIMEI()

#module.acquireGnssSettings()
file = open("gnss_log_600sec_AA.csv", "a")
file.write("Time,lattitude,longitude\n")

#----------------------------------------------------------------------------------------
#	get current geoposition
#----------------------------------------------------------------------------------------

while True:

    module.gnssOn()

    start_time = time.time()
    gpsloc = None
    while(not gpsloc):
        time.sleep(30.)
        module.sendATcmd('AT+QGPSGNMEA="GSV"')
        gpsloc = module.acquirePositionInfo()

    print ("position search time %s seconds" % int(time.time() - start_time))
    
    for sec in range (600):
        if gpsloc:
            mqtt_json = nmea2gps_json(gpsloc)
            csv_string = str(sec) + ";" + str(mqtt_json['latitude']) + ";" + str(mqtt_json['longitude'])
            file.write(csv_string.replace('.',',')+"\n")
            file.flush()
        time.sleep(.99)
        gpsloc = module.acquirePositionInfo()
        
    module.gnssOff()
    time.sleep(2.)

    #----------------------------------------------------------------------------------------
    #	send current geoposition to MQTT server
    #----------------------------------------------------------------------------------------

    mqtt_json = nmea2gps_json(gpsloc)
    print("https://maps.google.com/?q=%s,%s" % (mqtt_json['latitude'], mqtt_json['longitude']))
    mqtt_msg = json.dumps(mqtt_json)

    module.sendATcmd("AT+CMEE=2")
    module.sendATcmd("AT+CPIN?", "OK\r\n", 5)
    module.sendATcmd("AT+CFUN=1")
    module.sendATcmd("AT+CREG=0", "OK\r\n", 10)

    module.getSignalQuality()
    module.checkRegistration()
    module.sendATcmd("AT+QNWINFO", "OK\r\n", 10)

    contextID = "1"
    module.configTcpIpContext(contextID, "wsim")
    module.activatePdpContext(contextID, 5)

    mgtt_client_idx = "0"
    mqtt_client_id_string = module.IMEI
    module.openMqttConnection(mgtt_client_idx, mqtt_broker, mqtt_port)
    module.connectMqttClient(mqtt_client_id_string, mqtt_username, mqtt_password)

    module.publishMqttMessage(mqtt_topic, mqtt_msg)

    module.sendATcmd("AT+QMTDISC=0", "+QMTDISC:", 10)
    module.closeConnection()
    module.deactivatePdpContext(contextID, 5)

    time.sleep(2.)

module.close()

#51.229047, 6.714671 work
