<<<<<<< HEAD
from environment import Environment

env  = Environment(False)

state = env.reset()

for i in state:
    print(len(i), type(i[0]))
=======
import numpy as np
import pandas as pd
'''
road = np.load("data_files/jams2.npy")

for i in range(len(road)):
    for j in range(7):
        print("day", j,)
        for k in range(24):
            print("hour", k, ":", road[i][j][k])'''
data = np.load('data/data-1.npy')
df1 = pd.DataFrame(data)
print(df1.head())
>>>>>>> a0fcde1d51258f884eb23fee356898c338212e06
