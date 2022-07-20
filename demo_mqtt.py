'''
  demo_echo.py - This is basic Finamon GNSS/Modem BG770A UDP echo example.
'''
from BG770A import BG770A
import time
import random

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

mqtt_msg  = '''{
"imei": 866349041737515,
"latitude": 51.228997,
"longitude": 6.714182,
"utc":  1656934485
}'''

#mqtt_broker = 'broker.emqx.io'
#mqtt_port = 1883
#mqtt_topic = "qf4dcfae.eu-central-1.emqx.cloud"
## generate client ID with pub prefix randomly
#mqtt_client_id_string = f'python-mqtt-{random.randint(0, 1000)}'
#mqtt_username = 'finamon'
#mqtt_password = 'Finamon_2022'
#mqtt_msg = 'Hello MQTT from GPS-4G-HAT shield'


mqtt_broker = '23.88.108.59'
mqtt_port = 1883
mqtt_client_id_string = 'TBD'
mqtt_username = 'api'
mqtt_password = 'flake-iraq-contra'
mqtt_topic = "gps/coordinates"


module = BG770A()
module.debug_print("MQTT client demo")

module.sendATcmd("AT")
module.getHardwareInfo()
module.getFirmwareInfo()
module.getIMEI()

#module.acquireMqttSettings()

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
module.openMqttConnection(mgtt_client_idx, mqtt_broker, mqtt_port)
module.connectMqttClient(mqtt_client_id_string, mqtt_username, mqtt_password)
module.publishMqttMessage(mqtt_topic, mqtt_msg)

#module.subscribeToMqttTopic(mqtt_topic)
#print("wait message from topic: " + mqtt_topic)
#module.waitUnsolicited("+QMTRECV:", 60)
#module.unsubscribeFromMqttTopic(mqtt_topic)

module.sendATcmd("AT+QMTDISC=0", "+QMTDISC:", 10)
module.closeConnection()
module.deactivatePdpContext(contextID, 5)
module.close()



#[14:33:25] Finamon GNSS/Modem BG770A Shield created
#[14:33:25] MQTT client demo
#[14:33:25] AT...OK..
#[14:33:25] AT+CGMM...BG770A-GL....OK..
#[14:33:25] AT+CGMR...BG770AGLAAR01A03....OK..
#[14:33:26] AT+GSN...863593051995496....OK..
#[14:33:26] AT+CMEE=2...OK..
#[14:33:26] AT+CPIN?...+CPIN: READY....OK..
#[14:33:26] AT+CFUN=1...OK..
#[14:33:26] AT+CREG=0...OK..
#[14:33:27] AT+CSQ...+CSQ: 28,0....OK..
#[14:33:27] AT+QCSQ...+QCSQ: "eMTC",-56,-78,210,-9....OK..
#[14:33:27] AT+CEREG=0...OK..
#[14:33:27] AT+CEREG?...+CEREG: 0,5....OK..
#[14:33:28] AT+QNWINFO...+QNWINFO: "eMTC","26202","LTE BAND 20",6300....OK..
#[14:33:28] AT+QICSGP=1,1,"wsim","","",1...OK..
#[14:33:28] AT+QIACT=1...ERROR..
#[14:33:28] AT+QIACT?...+QIACT: 1,1,1,"10.3.118.130"....OK..
#[14:33:28] AT+QMTOPEN=0,"broker.emqx.io",1883...OK..
#[14:33:29] ..+QMTOPEN: 0,0..
#[14:33:29] AT+QMTOPEN?...+QMTOPEN: 0,"broker.emqx.io",1883....OK..
#[14:33:29] AT+QMTCONN=0,"python-mqtt-176","finamon","Finamon_2022"...OK..
#[14:33:29] ..+QMTCONN: 0,0,0..
#[14:33:29] AT+QMTPUB=0,1,1,0,"qf4dcfae.eu-central-1.emqx.cloud",33...>
#[14:33:30] Hello MQTT from GPS-4G-HAT shield..OK....+QMTPUB: 0,1,0..
#[14:33:30] AT+QMTSUB=0,1,"qf4dcfae.eu-central-1.emqx.cloud",2...OK..
#[14:33:30] ..+QMTSUB: 0,1,0,2..
#wait message from topic: qf4dcfae.eu-central-1.emqx.cloud
#[14:33:36] ..+QMTRECV: 0,0,"qf4dcfae.eu-central-1.emqx.cloud","hello GPS-4G-HAT shield"..
#[14:33:37] AT+QMTUNS=0,1,"qf4dcfae.eu-central-1.emqx.cloud"...OK..
#[14:33:37] ..+QMTUNS: 0,1,0..
#[14:33:37] AT+QMTDISC=0...OK....+QMTDISC: 0,0..
#[14:33:37] AT+QICLOSE=0...OK..
#[14:33:38] AT+QIDEACT=1...OK..
