import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pygame
from pygame import *
import time
import numpy as np
import random
from math import atan2,cos,pi,sin

c = (37.6193, 55.7506) # center
r_out = 0.0462
r_in = 0.0343
c_out = (37.6231, 55.7267)
c_in = (37.6536, 55.7504)
l_top = (37.5775, 55.7742)
r_bot = (37.66, 55.7261)
SCALE = 5200
fi = 55.75
LENGTH = 15600

print(((c[0] - c_out[0])**2 + (c[1] - c_out[1])**2)**0.5)
print(((c[0] - c_in[0])**2 + (c[1] - c_in[1])**2)**0.5)

df = pd.read_csv("data_files/filtered_all.csv",sep=",")

#del df[df["uuid"] in [74005, 93692, 104742]]

# 1511
#bad 74005 93692 104742
#kruk 82255 84710 99235 104657

# 1504
#bad
#kruk 80683 84442 84493 111948

colors = {}
ids = np.unique(df.uuid).tolist()
for id in ids:
    colors[id] =pygame.Color(random.randint(0,255),random.randint(0,255),random.randint(0,255))
print(ids)
'''for id in ids:
    df1 = df[df.uuid == id]#[ df.y > 55.7][df.y < 55.8][df.x > 37.4][df.x < 37.7]
    x = df1.x
    y = df1.y
    plt.scatter(x,y,)
    print(id)
    plt.show()'''


df_stops = pd.read_csv("data_files/koordinaty_ostanovok12.csv")
stops = [(i.x, i.y) for _,i in df_stops.iterrows()]
print(stops)

np.random.shuffle(ids)
df1 = df#[df.uuid == ids[0]]
pygame.init()
DISPLAY = (800, 640)  # Группируем ширину и высоту в одну переменную
screen = pygame.display.set_mode(DISPLAY)
pygame.display.set_caption("Super Mario Boy")
bg = Surface(DISPLAY)
BACKGROUND_COLOR = "#005500"

bg.fill(Color(BACKGROUND_COLOR))

img = pygame.image.load("pictures/map.jpg")
#img = pygame.image.load("vibrosi.jpg")
#screen.blit(img, (0, 0))

#np.random.shuffle(df1)



def cart2pol(x,y):
    return (x**2+y**2)**0.5, atan2(y, x)

def pol2cart(r,fi):
    return r*cos(fi),r*sin(fi)

last_coordinate = [0 for i in range(len(ids))]
screen.blit(img, (-100, 0))
start = 1000
for _,i in df1.iterrows():
    if _%50==0:
        pass#screen.blit(img, (-100, 0))
    #if  _ > 4000  or _ < 3000:
     #   continue

    for e in pygame.event.get():  # Обрабатываем события
        if e.type == QUIT:
            raise (SystemExit, "QUIT")

    '''for stop in stops:
        pf = Surface((12, 12))
        color = pygame.Color("#FF0000")
        pf.fill(color)
        coord = ((stop[0] - 37.5) * 5000, (stop[1] - 55.7) * 5000)
        screen.blit(pf, coord)
    '''

    lc = last_coordinate[ids.index(i.uuid)]
    z = ((-atan2(-(i.y-c[1])/cos(55*pi/180), i.x-c[0]))/(2*pi)*LENGTH)%LENGTH
    last_coordinate[ids.index(i.uuid)] = z
    if z - lc > 5 or z - lc < -600:
        continue

    pf = Surface((8, 8))
    color = colors[i.uuid]#pygame.Color(random.randint(0,255),random.randint(0,255),random.randint(0,255))
    pf.fill(color)
    coord = ((i.x-c[0])*SCALE+450, -(i.y-c[1])/cos(fi*pi/180)*SCALE+350)
    screen.blit(pf, coord)
    #print(coord)

    # Center
    pf = Surface((20, 20))
    color = pygame.Color("#FF00FF")
    pf.fill(color)
    coord = ((c[0] - c[0]) * SCALE + 450, -(c[1] - c[1]) / cos(fi * pi / 180) * SCALE + 350)
    screen.blit(pf, coord)

    coord = ((i.x-c[0])*SCALE+450, -(i.y-c[1])/cos(fi*pi/180)*SCALE+350)
    print(i.x-c[0], -(i.y-c[1]))

    '''for j1 in np.arange(r_bot[1]-0.1, l_top[1]+0.1, 0.0001):
        i1 = c[0] - (r_in**2 - (c[1] - j1) ** 2)**0.5
        pf = Surface((1, 1))
        color = pygame.Color("#FF00FF")
        pf.fill(color)
        coord = ((i1 - c[0]) * 5000 + 450, -(j1 - c[1])* 5000 + 350)
        try:
            screen.blit(pf, coord)
        except:
            pass

        i1 = c[0] + (r_in**2 - (c[1] - j1) ** 2)**0.5
        pf = Surface((1, 1))
        color = pygame.Color("#FF00FF")
        pf.fill(color)
        coord = ((i1 - c[0]) * 5000 + 450, -(j1 - c[1])* 5000 + 350)
        try:
            screen.blit(pf, coord)
        except:
            pass'''

    '''    for i1 in np.arange(l_top[0], r_bot[0], 0.001):
            for j1 in np.arange(r_bot[1], l_top[1], 0.001):
                r = ((c[0] - i1)**2 + (c[1] - j1)**2)**0.5
                print(r, r_in, r_out)
                if True or r > r_in and r < r_out:
                    pf = Surface((1, 1))
                    color = pygame.Color("#FF00FF")
                    pf.fill(color)
                    coord = ((i1 - c[0]) * 5000 + 450, -(j1 - c[1]) / cos(55 * pi / 180) * 5000 + 350)
                    screen.blit(pf, coord)
'''
    fontObj = pygame.font.Font('freesansbold.ttf', 30)
    textSurfaceObj = fontObj.render('Real time: {}'.format(i.t), True, Color("#FFFF00"),
                                    Color("#0000FF"))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (200, 30)

    screen.blit(textSurfaceObj, textRectObj)

    pygame.display.update()

    #if _ > start:
    #    time.sleep(1)

#df = df#[df.uuid == 84493]


