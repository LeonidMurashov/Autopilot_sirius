import pandas as pd
import numpy as np
import pygame
from pygame import *
from math import *
import theano
import theano.tensor as T
df_traffic = pd.read_csv('Skorost.csv', sep=";")
df_stop = pd.read_csv('Ostanovki.csv', sep=';')
df_lights = pd.read_csv('Svetofory.csv', sep=';')

ring = []
len_ring = 17016
num_ring = 1418
num_buses = 40
DISPLAY = (800, 640)


class Bus:
    def __init__(self, id, speed, coord):
        self.id = id
        self.coord = coord
        self.speed = speed
        self.wait_time = 0
        self.length = 0
        self.dist = 0

    def change_pos(self, index):
        ring[index[self.coord]].is_bus = True
        step = self.coord * 0.28 + self.coord
        if step > (self.coord + 12):
            ring[index[self.coord]].is_bus = False
            self.dist = step - (self.coord+12)
            if step < 17015:
                self.coord += 12
            else:
                self.coord = 23
            ring[index[self.coord]].is_bus = True
        else:
            self.dist = step - self.coord
        try:
            stop = ring[index[self.coord]].stop.wait_time
        except:
            stop = 0
        try:
            light = ring[index[self.coord]].light.wait_time
        except:
            light = 0
        self.speed = int(ring[index[self.coord]].traffic)
        self.wait_time = int(stop) + int(light)


class Stop:
    def __init__(self, coord, time):
        self.coord = coord
        self.time_lost = 0
        self.wait_time = time

    def update(self):
        if ring[index[self.coord]].is_bus:
            self.wait_time = 15
            self.time_lost = 0
        else:
            self.time_lost += 1
            if self.time_lost > 600:
                self.wait_time += 1


class Light:
    def __init__(self, coord, red, green, now):
        self.red = red
        self.green = green
        self.coord = coord
        self.light = now
        self.isred = True if self.light > self.red else False
        self.wait_time = 0 if self.isred == False else self.light

    def update(self):
        if self.light < self.green + self.red:
            self.light += 1
            self.isred = True if self.light > self.red else False
            self.wait_time = 0 if self.isred == False else self.light
        else:
            self.light = 0
            self.isred = True
            self.wait_time = self.red

class Road:
    def __init__(self, stop, light, traffic_jam):
        self.stop = stop
        self.light = light
        self.traffic = traffic_jam
        self.is_bus = False


def traffic(coord):
    speed = df_traffic[df_traffic['end'] == coord].v
    return speed

def coordinate_to_circle(z, r = 200):
    z = z/len_ring*2*pi
    return(cos(z)*r + 300, sin(z)*r + 300)


buses = df_stop[df_stop.busstop == "y"]
lights = df_lights[df_lights.light == "y"]
buses_units = []


speed_data = T.scalar(dtype="int32")
func2 = 5 / speed_data * 255
func2 = speed_data / 80 * 255

comp1 = theano.function(speed_data. func1, allow_input_downcast=True)
comp2 = theano.function(speed_data, func2, allow_input_downcast=True)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption("System")
    bg = Surface(DISPLAY)
    BACKGROUND_COLOR = "#00CC66"
    bg.fill(Color(BACKGROUND_COLOR))
    PLATFORM_COLOR = "#555555"
    BUS_COLOR = "#9999FF"
    a = []
    j = 0
    index = {}
    for i in range(11, len_ring, 12):
        a.append(i)
        index[i] = j
        j += 1
        speed = traffic(i)
        if i in np.array(buses.end):
            stop = Stop(i, buses[buses.end == i].time)
        else:
            stop = None
        if i in np.array(lights.end):
            light = Light(i, int(lights[lights.end == i].red),
                          int(lights[lights.end == i].green), int(lights[lights.end == i].now))
        else:
            light = None
        ring.append(Road(stop, light, speed))

    np.random.shuffle(a)
    buses_first_coords = a[:num_buses]
    bus_id = 0
    for i in list(buses_first_coords):
        b_speed = ring[index[i]].traffic
        buses_units.append(Bus(bus_id, b_speed, i))
        bus_id +=1
    speed_voc = {}
    for i in range(11, len_ring, 12):
        speed_voc[i] = traffic(i)
    while True:

        for e in pygame.event.get():  # Обрабатываем события
            if e.type == QUIT:
                raise (SystemExit, "QUIT")

        for i in range(11, len_ring, 12):
            pf = Surface((10, 10))
            speed = speed_voc[i]
            color = pygame.Color(int(comp1(speed)), int(comp2(speed)), 0)
            pf.fill(color)
            screen.blit(pf, coordinate_to_circle(i))

        for bus in buses_units:
            pf = Surface((12, 12))
            pf.fill(Color("#000000"))
            screen.blit(pf, coordinate_to_circle(bus.coord))
            if bus.wait_time == 0:
                print("id:", bus.id, 'скорость:', int(bus.speed), "координаты: " , int(bus.coord))
                bus.change_pos(index)

            else:
                print("id:", bus.id, "ждём", bus.wait_time, 'координаты:',int(bus.coord))
                bus.wait_time -= 1
            pf = Surface((12, 12))
            pf.fill(Color(BUS_COLOR))
            screen.blit(pf, coordinate_to_circle(bus.coord))

        for road in ring:
            if road.light is not None:
                road.light.update()
                pf = Surface((20, 20))
                color = Color("#FF0000") if road.light.light > road.light.red else Color("#00FF00")
                pf.fill(color)
                screen.blit(pf, coordinate_to_circle(road.light.coord, 250))
                #print("есть светофор на : ", road.light.coord, 'наличие остановки:', road.stop, )
            if road.stop is not None:
                pf = Surface((8, 8))
                no_bus = road.stop.time_lost if road.stop.time_lost != 0 else 0.01
                color = pygame.Color(max(int(min(255, no_bus / 600 * 255)), 0),
                                     max(int(min(255, 255 * 60 / no_bus * 1)), 0), 0)
                pf.fill(color)
                screen.blit(pf, coordinate_to_circle(road.stop.coord, 180))
                road.stop.update()
                #print("есть остановка на: ",road.stop.coord, "наличие светофора:", road.light)

        pygame.display.update()









