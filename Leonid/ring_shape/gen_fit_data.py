from math import atan2,cos,pi,sin
import numpy as np
c = (37.6193, 55.7506) # center

x,y = [],[]
with open("coordinates.txt") as file:
    for i in file:
        a = list(map(float, i.split()))
        x.append(a[0])
        y.append(a[1])

z = [ -atan2(y[i]/cos(c[1]*pi/180), x[i]) for i in range(len(x))]

print(z)

dots = list(zip(x,y,z))[:100]
print(dots)
dots = sorted(dots, key=lambda x: x[2])

def cart2pol(x,y):
    return (x**2+y**2)**0.5, atan2(y, x)

values = []

r0, fi0 = cart2pol(dots[0][0], dots[0][1])
#print(3.15, 1)
for i in dots:
    r, fi = cart2pol(-i[0], i[1]/cos(c[1]*pi/180))
    #print(fi, r/r0)#(fi)%(2*pi)-pi, r/r0)
    values.append([fi, r/r0])
#print(0,1)
values.append([-3.15, 1])
values.append([3.15, 1])
#print(-3.15, 1)

# Go with filter
filter = [0,0,1,0,0]
#filter = [0.1,0.1,0.1,0.3,0.1,0.1,0.1]
#filter = [0.333]*3

def check_index(ind):
    return ind if ind < len(values) else ind % len(values)

values_new = [0 for i in range(len(values))]
with open("fit_data.txt", "w") as file:
    for i in range(len(values)):
        values_new[i] = [values[i][0], sum([values[check_index(i + j - len(filter)//2)][1]*filter[j] for j in range(len(filter))])]
        file.write("{} {}\n".format(values_new[i][0], values_new[i][1]))
        print(values_new[i][0], values_new[i][1])



