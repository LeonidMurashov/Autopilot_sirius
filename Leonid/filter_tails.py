#install shapely http://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely
import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from math import atan2,cos,pi,sin
import numpy as np

LENGTH = 15600

df_tracks = pd.read_csv("data_files/trbusB1504.csv", sep=";")
df_tracks2 =  pd.read_csv("data_files/trbusB1511.csv", sep=";")
df_tracks = pd.concat([df_tracks, df_tracks2], ignore_index=True)
print("All len:", len(df_tracks))

df_stops = pd.read_csv("data_files/koordinaty_ostanovok12.csv")

c = (37.6193, 55.7506) # center

length = len(df_tracks)
df_tracks.pop("route")

x, y = df_stops.x, df_stops.y
z = [((-atan2(-(y[i]-c[1])/cos(55*pi/180), x[i]-c[0]))/(2*pi)*LENGTH)%LENGTH for i in range(len(x))]

stops = [[i.x, i.y, z[_]] for _,i in df_stops.iterrows()]
stops = sorted(stops,key=lambda x: x[2])
points = [(i[0], i[1]) for i in stops]

def cart2pol(x,y):
    return (x**2+y**2)**0.5, atan2(y, x)

def pol2cart(r,fi):
    return r*cos(fi),r*sin(fi)

caret = 0.0025
points_in = []
points_out = []
for stop in stops:
    r, fi = cart2pol(stop[0]-c[0], stop[1]-c[1])
    x1, y1 = pol2cart(r-caret, fi)
    x2, y2 = pol2cart(r+caret, fi)
    x1 += c[0]; x2 += c[0]; y1 += c[1]; y2 += c[1]
    points_in.append((x1, y1))
    points_out.append((x2, y2))
poly_in = Polygon(points_in)
poly_out = Polygon(points_out)

print(points_in)

del_arr = []
for _,i in df_tracks.iterrows():
    point = Point(i.x, i.y)
    if (poly_in.contains(point) or not poly_out.contains(point)):
        del_arr.append(_)
    if _ % 1000 == 0:
        print(_/length)
print(del_arr)
df_tracks = df_tracks.drop(del_arr)

df_tracks.to_csv("data_files/filtered_all.csv")
print()
print("Deleted", (length - len(df_tracks))/length)



