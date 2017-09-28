import pandas as pd
from math import atan2, pi, cos

c = (37.6193, 55.7506) # center
LENGTH = 15600
df = pd.read_csv("koordinaty_ostanovok12.csv")

x, y = df.x, df.y

del df["x"]
del df['y']
del df["id"]

z = [((-atan2(-(y[i]-c[1])/cos(55*pi/180), x[i]-c[0]))/(2*pi)*LENGTH)%LENGTH for i in range(len(x))]
df.insert(len(df.columns), "coordinate", z)
print(df)
#df.to_csv("converted.csv", encoding="utf-8")

