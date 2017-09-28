import numpy as np
import matplotlib.pyplot as plt

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def moving_average2(a) :
    return np.ma.average(a)

np.ma.average

x1 = np.arange(50)
y1 = np.zeros(50)
y1[5] = 2
y1[7] = 3
y1[11] = 1
y1[20] = 10
y1[21] = 10
y2 = []
#y3 = y2

for i in range(len(y1)):
	y2.append(moving_average2(y1[max(i-7, 0):i]))

arr = [(x1,y1), (x1,y2)]
for i in arr:
    plt.plot(i[0], i[1])
plt.show()