
from math import atan2,cos,pi,sin
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle

LENGTH = 1000

def cart2pol(x,y):
    return (x**2+y**2)**0.5, atan2(y, x)

def pol2cart(r,fi):
    return r*cos(fi),r*sin(fi)

coords = []
pol_coords = []

x,y = [],[]
with open("fit_data.txt") as file:
    for _,i in enumerate(file):
        a,b = map(float,i.split())
        x.append(a)
        y.append(b)

from scipy import interpolate
f = interpolate.interp1d(x, y,)

#save
with open('ring_function.pickle', 'wb') as file2:
    pickle.dump(f, file2)


c = len(x)

def coordinate_to_circle(z, offset = 0):
    z = z/LENGTH*2*pi
    print(z)
    non_linearity = f((z+pi)%(2*pi)-pi)
    return cos(-z)*(300+offset)*non_linearity + 500, sin(-z)*(300+offset)*non_linearity + 500

x1 = []
y1 = []
for i in range(1000):
    a,b = coordinate_to_circle(i)
    x1.append(a)
    y1.append(b)

plt.scatter(x1,y1)
plt.show()

