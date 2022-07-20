import csv
import math
import gmplot
import pynmea2


def haversine(coord1, coord2):
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2) 
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))



org_lat = 51.229137
org_lon = 6.714244

#org_lat = 51.434020
#org_lon = 6.759148
#file_name = "knuellenmarkt"

file_name = "nmea_drive"
file = open(file_name + '.log', encoding='utf-8')

lat = []
lon = []
#time = []
num = 0
avg_lat = 0
avg_lon = 0

for line in file.readlines():
    try:
        msg = pynmea2.parse(line)
        if msg.sentence_type == 'GGA' and msg.lat:
            #time.append(msg.data[0])
            lat.append(msg.latitude)
            avg_lat += msg.latitude
            lon.append(msg.longitude)
            avg_lon += msg.longitude
            num += 1
            #print(repr(msg))
    except pynmea2.ParseError as e:
        print('Parse error: {}'.format(e))
        continue

avg_lat /= num
avg_lon /= num


file.close()

print(num, avg_lat, avg_lon)

out_file = file_name + '.csv'
f = open(out_file, 'w', newline='')
f.write('nr;lat;long\n')

for k in range (len(lat)):
    x = round(haversine((avg_lat, avg_lon), (lat[k], avg_lon)), 1)
    if avg_lat > lat[k]:
        x = -x

    y = round(haversine((avg_lat, avg_lon), (avg_lat, lon[k])), 1)
    if avg_lon > lon[k]:
        y = -y

    print(k, x, y, round(math.sqrt(x*x + y*y), 1))
    f.write(str(k) + ';' + str(x).replace('.',',') + ';' + str(y).replace('.',',') + '\n')

f.close()

#print (round(haversine((org_lat, org_lon), (avg_lat, org_lon)), 1),
#       round(haversine((org_lat, org_lon), (org_lat, avg_lon)), 1))

apikey = 'AIzaSyDrKSCXw-YDdKg76o_W-3FVubCZQ-8P9JI'
drive_map = gmplot.GoogleMapPlotter(
    avg_lat, 
    avg_lon, 
    12, apikey=apikey)

drive_map.marker(lat[0],  lon[0])
drive_map.marker(lat[-1], lon[-1])

drive_map.plot(lat, lon, color = 'magenta',  edge_width = 2.5)
drive_map.scatter(lat, lon, marker = False, size = 5)

drive_map.draw( "drive_map12.html" )

