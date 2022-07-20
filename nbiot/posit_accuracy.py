import sys
import csv

import pandas as pd
#import gmplot

import math

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


meas = [
    #Gemalto
    ("G17_1214.CSV", "green"),
    ("G33_1023.CSV", "green"),
    ("G64_1049.CSV", "green"),
    #Quectel
    ("Q06_1335.CSV", "blue"),
    ("Q15_1403.CSV", "blue"),
    ("Q93_1431.CSV", "blue"),
    ("Q42_1521.CSV", "blue"),
    ("Q29_1557.CSV", "blue"),
    #Telit
    ("T31_0822.CSV", "brown"),
    ("T81_0955.CSV", "brown"),
    ("T84_1023.CSV", "brown"),
    ("T98_1049.CSV", "brown"),
    ("T23_1130.CSV", "brown"),

    ("T98_1300.CSV", "red"),

]

#org_lat = 51.238736 
#org_lon = 6.722845

#org_lat = 51.434286     # home DU
#org_lon = 6.758511

org_lat = 51.2290282      # work DÜ
org_lon =  6.7146821

d_lat = .00005
d_lon = .0005

for x in range (-5, 5):
    step = round(x * d_lat, 6)
    print(step, round(haversine((org_lat, org_lon), (org_lat + step, org_lon)), 1))

for y in range (-5, 5):
    step = round(y * d_lon, 6)
    print(step, round(haversine((org_lat, org_lon), (org_lat + step, org_lon)), 1))

log_file = "gnss_log_600sec_AA.log"
out_file = "gnss_log_600sec_m.csv"

coord = pd.read_csv(log_file)

header = ['nr', 'lat', 'long', 'dist']

# open the file in the write mode
f = open(out_file, 'w', newline='')

# create the csv writer
writer = csv.writer(f, delimiter=';')

writer.writerow(header)

for k in range (len(coord)):
    #dist = haversine((org_lat, org_lon), (coord["latitude"].iloc[k], coord["longitude"].iloc[k]))
    x = round(haversine((org_lat, org_lon), (coord["latitude"].iloc[k], org_lon)), 1)
    if org_lat > coord["latitude"].iloc[k]:
        x = -x

    y = round(haversine((org_lat, org_lon), (org_lat, coord["longitude"].iloc[k])), 1)
    if org_lon > coord["longitude"].iloc[k]:
        y = -y

    print(x, y, math.sqrt(x*x + y*y))
    #lat = str(round(coord["latitude"].iloc[k], 6))
    #lon = str(round(coord["longitude"].iloc[k], 6))

    writer.writerow([coord["Time"].iloc[k], str(x).replace('.',','), str(y).replace('.',',')])


#apikey = 'AIzaSyDrKSCXw-YDdKg76o_W-3FVubCZQ-8P9JI'
#mymap = gmplot.GoogleMapPlotter(
#    org_lat,    #min_lat + (max_lat - min_lat) / 2, 
#    org_lon,    #min_lon + (max_lon - min_lon) / 2, 
#    19, apikey=apikey)

#mymap.marker(org_lat, org_lon)

#mymap.circle(org_lat, org_lon, 10, edge_alpha=.0, face_alpha=.15)
#mymap.circle(org_lat, org_lon, 20, edge_alpha=.0, face_alpha=.1)

#for i in range (len(meas)):
#    coord = pd.read_csv("C:/Projects/NextGen/Tests/Accuracy_GNSS/" + meas[i][0])
#    mymap.plot(coord.latitude, coord.longitude, meas[i][1], edge_width=2)
#    #mymap.scatter(coord.latitude, coord.longitude, meas[i][1], 1, False, symbol='o')

#    min_dist = 1000.
#    moment = 0 
#    for k in range (len(coord)):
#        dist = haversine((org_lat, org_lon), (coord["latitude"].iloc[k], coord["longitude"].iloc[k]))
#        if (dist < min_dist):
#            min_dist = dist
#            moment = k 

#    dist = haversine((org_lat, org_lon), (coord["latitude"].iloc[-1], coord["longitude"].iloc[-1]))
#    print(meas[i][0], int(dist + .5), int(min_dist+.5), moment)

#map_file = "C:/Projects/NextGen/Tests/Accuracy_GNSS/all_modems.html"
#mymap.draw(map_file)


