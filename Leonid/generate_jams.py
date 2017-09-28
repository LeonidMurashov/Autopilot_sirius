import pandas as pd
import numpy as np
from math import atan2,cos,pi,sin
import datetime, time

LENGTH = 15600
c = (37.6193, 55.7506) # center
df_traffic = pd.read_csv("data_files/filtered_all.csv")
ids = np.unique(df_traffic.uuid)

def get_secs(str):
    tm = datetime.datetime.strptime(str, "%H:%M:%S").time()
    return tm.second + tm.minute*60 + tm.hour*3600

def get_week_day(str):
    tm = datetime.datetime.strptime(str, "%Y-%M-%d").date()
    return (tm.weekday()+1) % 7 # 0 - Monday

x, y = df_traffic.x, df_traffic.y
times, dates = df_traffic.t, df_traffic.dt
del df_traffic["x"]
del df_traffic['y']
z = [((-atan2(-(y[i]-c[1])/cos(55*pi/180), x[i]-c[0]))/(2*pi)*LENGTH)%LENGTH for i in range(len(x))]
seconds = [get_secs(i) for i in times]
week_days = [get_week_day(i) for i in dates]

df_traffic.insert(len(df_traffic.columns), "dot", z)
df_traffic.insert(len(df_traffic.columns), "secs", seconds)
df_traffic.insert(len(df_traffic.columns), "week_day", week_days)

print(df_traffic.head())
that_day = df_traffic.iloc[325227]['dt']

road = []
for i in range(LENGTH//10):
    road.append([])
    for j in range(7):
        road[i].append([])
        for k in range(24):
            road[i][j].append([])

odd = 0
for _,id in enumerate(ids):
    df = df_traffic[df_traffic.uuid == id]
    for i in range(len(df)-1):
        if not df.iloc[i]['dt'] == that_day:
            continue
        t = df.iloc[i+1].secs - df.iloc[i].secs
        # Get hour
        tm = datetime.datetime.strptime(df.iloc[i+1].t, "%H:%M:%S").time()
        hour = (tm.hour+3)%24 # TODO Solve hours+3
        week_day = df.iloc[i+1].week_day

        if t > 40 or t < 5:
            odd += 1
            continue

        c1, c2 = df.iloc[i]["dot"], df.iloc[i+1]["dot"]
        x1, x2 = c1, c2

        # Catch buses near 0
        if LENGTH*0.95 < abs(x2 - x1) < LENGTH*1.05:
            x1 = (x1 + LENGTH / 2) % LENGTH
            x2 = (x2 + LENGTH / 2) % LENGTH
            a= 0
        s = x2 - x1
        #Crop negative TODO me
        if s < 0 or s == 0 or s/t/1000*3600 > 100:
            continue

        # Catch buses near 0
        if c2 - c1 > 0:
            for j in range(int(c1//10), int(c2//10)):
                road[j][week_day][hour].append(s/t/1000*3600)
        else:
            for j in range(int(0//10), int(c2//10)):
                road[j][week_day][hour].append(s/t/1000*3600)
            for j in range(int(c1//10), int(LENGTH//10)):
                road[j][week_day][hour].append(s/t/1000*3600)

    print("{} done".format(_/len(ids)))

T = 0
nan = 0
for i in range(len(road)):
    for j in range(7):
        print("day", j,)
        for k in range(24):
            road[i][j][k] = np.mean(road[i][j][k])
            print("hour", k, ":", road[i][j][k])
            if road[i][j][k] != road[i][j][k]:
                nan += 1
print("NaNs in data:", nan, nan/(len(road)*24*7))
print("Skipped:", round(odd/len(df_traffic),3))

np.save("data_files/jams_test.npy", road)
'''with open("data_files/jams2.csv", "w") as file:
    file.write("v\n")
    for i in road:
        file.write(str(i))
        file.write("\n")
print("Saved.")'''