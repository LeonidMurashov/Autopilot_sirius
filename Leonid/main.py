import random
import pandas as pd
import pygame
from pygame import *
import time
from math import cos, sin, pi
import numpy as np

# Py game consts
DISPLAY = (1000, 700)  # Группируем ширину и высоту в одну переменную

lights = []
stops = []
road = []
buses = []
TIME = 0
GLOBAL_TIME = 0
LENGTH = 15600
PERIOD = 2
BUSES_COUNT = 15
DAY = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

DISPLAY_ACTION = True#True
DISPLAY_TRAFFIC = True
pygame.init()
screen = pygame.display.set_mode(DISPLAY)

class Light:
    def __init__(self, red, green, coordinate): # 0-10 red and 11-20 green
        self.red = red
        self.green = green
        self.iterator = random.randint(0, red + green-1)
        self.coordinate = coordinate

    def step(self):
        self.iterator = (self.iterator + PERIOD) % (self.red + self.green)

    def can_go(self):
        return self.red - self.iterator < 0

class Stop:
    def __init__(self, coordinate):
        self.coordinate = coordinate
        self.no_bus_time = 0
        self.with_bus_time = 0
        self.bus_stack = []

    def add_bus(self, bus):
        self.bus_stack.append(bus)
        if len(self.bus_stack) == 1:
            self.with_bus_time = min(5*60, 15 if self.no_bus_time < 8 * 60 else 15 + (self.no_bus_time - 8 * 60)/20)
        self.no_bus_time = 0

    def can_go(self, bus):
        return (not bus in self.bus_stack)# or\
               #self.bus_stack.index(bus) >= 3

    def step(self):
        if self.with_bus_time != 0:
            self.with_bus_time = max(0, self.with_bus_time - PERIOD)
            return
        if len(self.bus_stack) != 0:
            self.bus_stack[0].can_go = True
            self.bus_stack.pop(0)
            if len(self.bus_stack) != 0:
                self.with_bus_time = 15
                return
        self.no_bus_time += PERIOD


class Bus:
    def __init__(self, coordinate):
        self.coordinate = coordinate
        self.last_stop = get_prev_stop(coordinate)
        self.last_light = get_prev_light(coordinate)
        self.stop_time = 0
        self.can_go = True
        self.speed = 0

    def step(self, prev, next):
        if self.stop_time != 0:
            self.stop_time = max(0, self.stop_time - PERIOD)
            return
        if not self.last_stop.can_go(self):
            self.can_go = False
            return

        prev_stop = get_prev_stop(self.coordinate)
        prev_light = get_prev_light(self.coordinate)

        # Check if we stay at street light
        if prev_light != self.last_light:
            if not prev_light.can_go():
                self.can_go = False
                return
            else:
                self.last_light = prev_light
        self.can_go = True

        # {% yaroslav %}
        dist1 = LENGTH - prev + self.coordinate if self.coordinate < prev else self.coordinate - prev
        dist2 = LENGTH - self.coordinate + next if self.coordinate > next else next - self.coordinate
        dist = [dist1, dist2]
        dist.append(get_speed(prev))
        dist.append(get_speed(next))
        # if dist[0] > 200:
        #     dist[2]= [get_speed(i) for i in range(int(dist[0]), int(self.coordinate), 99)]
        #     dist[2] = int(np.mean(dist[2]))
        # if dist[1] > 200:
        #     dist[3] = [get_speed(i) for i in range(int(dist[0]), int(self.coordinate), 99)]
        #     dist[3] = int(np.mean(dist[3]))
        time = [int(dist[0] / dist[2]), int(dist[1] / dist[3])]
        if time[0] - time[1] > 10:
            #length = (time[0] - time[1] / 2) * dist[2]
            self.speed += 8  # (2 * length - 1.2 * (10 ** 2)) / (2 * 10)
        elif time[1] - time[0] > 10:
            #length = (time[1] - time[0] / 2) * dist[3]
            self.speed += 5  # (2 * length - 1.2 * (10 ** 2)) / (2 * 10)
        # {% end yaroslav %}

        self.max_speed = get_speed(self.coordinate)*0.27
        brake_dist = 3/2 * (self.speed)**2/ 1.2
        # Check if we need accel or stop
        dist_next = prev_stop.next.coordinate - self.coordinate if prev_stop.next.coordinate > self.coordinate else LENGTH + prev_stop.next.coordinate - self.coordinate
        if dist_next < brake_dist: #FIX ME
            accel = -1.2
        else:
            accel = 1.3

        if self.speed + accel*PERIOD > self.max_speed:
            self.speed = self.max_speed
        else:
            self.speed += accel*PERIOD

        if self.speed < 0:
            self.speed = 0

        self.coordinate = (self.coordinate + self.speed*PERIOD)%LENGTH
        if prev_stop != self.last_stop:
            self.last_stop = prev_stop
            prev_stop.add_bus(self)

def get_hour():
    return int((TIME-int(TIME/(3600*24))*24*3600 - TIME%3600)/3600)
def get_weekday():
    return int(TIME/(3600*24))

# Look at traffic jams
def get_speed(coordinate):
    index = int(coordinate/LENGTH*len(road)) # TODO check it
    hour = get_hour()
    speed = road[index][get_weekday()][hour]
    return speed if speed == speed else 60

def get_prev_stop(coordinate):
    for stop in stops[::-1]:
        if stop.coordinate < coordinate:
            return stop
    if len(stops) > 0:
        return stops[len(stops)-1]
    return None

def get_prev_light(coordinate):
    for light in lights[::-1]:
        if light.coordinate < coordinate:
            return light
    if len(lights) > 0:
        return lights[len(lights)-1]
    else:
        return None

'''def coordinate_to_circle(z, offset = 0):
    z = z/LENGTH*2*pi
    return(cos(-z)*(300+offset) + 500, sin(-z)*(300+offset) + 500)
'''

# Non-linearity
import pickle
with open('ring_shape/ring_function.pickle', 'rb') as f:
    function = pickle.load(f)

def coordinate_to_circle(z, width, offset=0):
    z = z/LENGTH*2*pi
    non_linearity = function(((z))%(2*pi)-pi)#get_nonlinearity((z/2/pi)*c)  *(TIME/60)
    return(cos(-z)*(212+offset)*non_linearity + 500 - width/2, sin(-z)*(212+offset)*non_linearity + 400 - width/2)

def draw_rect(z, size, color, offset=0):
    pf = Surface((size,size))
    pf.fill(color)
    screen.blit(pf,coordinate_to_circle(z, size, offset))

if __name__ == "__main__":
    # PyGame init
    pygame.display.set_caption("Super Mario Boy")
    bg = Surface(DISPLAY)
    BACKGROUND_COLOR = "#555555"
    bg.fill(Color(BACKGROUND_COLOR))
    PLATFORM_COLOR = "#555555"
    BUS_COLOR = "#0000FF"

    background = pygame.image.load("pictures/moscow_main.jpg")
    #matreshka = pygame.image.load("pictures/matreshka.png")
    df_lights = pd.read_csv("data_files/street_lights_converted.csv")
    df_stops = pd.read_csv("data_files/stops_converted.csv")
    road = np.load("data_files/jams.npy")

    for _, i in df_lights.iterrows():
        lights.append(Light(i["red"], i["green"], i["dot"]))
    lights = sorted(lights, key=lambda x: x.coordinate)

    for _, i in df_stops.iterrows():
        stops.append(Stop(i["dot"]))
    #stops.append(Stop(0))
    #stops.append(Stop(10000))
    stops = sorted(stops, key=lambda x: x.coordinate)
    for i in range(len(stops)):
        stops[i].next = stops[(i+1) % len(stops)]

    #buses = [Bus(random.randint(0, LENGTH-1)) for i in range(0, BUSES_COUNT*100, 100)]
    buses = [Bus(i) for i in range(0, BUSES_COUNT*500, 500)]

    TIME = 12*3600#random.randint(0, 24*7*3600)
    KPI = [0,0]

    # Main cycle
    while True:
        for light in lights:
            light.step()
        for stop in stops:
            stop.step()
        # {% yaroslav %}
        buses = sorted(buses, key=lambda x: x.coordinate)
        for i in range(0, len(buses)):
            buses[i].step(buses[(i - 1) % len(buses)].coordinate, buses[(i + 1) % len(buses)].coordinate)
            # {% end yaroslav %}
            # for bus in buses:
            #     bus.step()

        if GLOBAL_TIME > 60*60:#DISPLAY_ACTION:
            for e in pygame.event.get(): # Обрабатываем события
                if e.type == QUIT:
                    raise (SystemExit, "QUIT")

            #screen.blit(bg, (0, 0))
            screen.blit(background, (-339, -50))# Каждую грёбаную итерацию необходимо всё перерисовывать

            if DISPLAY_TRAFFIC:
                for i in range(0, LENGTH, 30):
                      draw_rect(i, 7, pygame.Color(50,50,50))

                for i in range(0, LENGTH, 30):
                      speed = get_speed(i)
                      color = pygame.Color(255,0,0) if speed < 17 else ( pygame.Color(0,150,0) if speed > 33 else pygame.Color(245,245,0))
                      draw_rect(i, 5, color)

            for bus in buses:
                draw_rect(bus.coordinate, 12, Color(BUS_COLOR))

            for light in lights:
                  color = Color("#00FF00") if light.can_go() else Color("#FF0000")
                  draw_rect(light.coordinate, 20, color, 30)

            for stop in stops:
                no_bus = stop.no_bus_time if stop.no_bus_time != 0 else 0.01
                color = pygame.Color(max(int(min(255, no_bus/600*255)), 0), max(int(min(255, 255*60/no_bus*1)),0), 0)
                draw_rect(stop.coordinate, 8, color, -30)

            # Get and display KPI
            fontObj = pygame.font.Font('freesansbold.ttf', 40)
            textSurfaceObj = fontObj.render('Ожидание: {} сек.'.format(round(KPI[0])), True, Color("#FFFF00"), Color("#0000FF"))
            textRectObj = textSurfaceObj.get_rect()
            textRectObj.center = (250, 30)
            screen.blit(textSurfaceObj, textRectObj)

            fontObj = pygame.font.Font('freesansbold.ttf', 40)
            textSurfaceObj = fontObj.render('{}:{} {}'.format(get_hour(), int(TIME%3600//60), DAY[get_weekday()]), True, Color("#FFFF00"), Color("#0000FF"))
            textRectObj = textSurfaceObj.get_rect()
            textRectObj.center = (DISPLAY[0]-200, 30)
            screen.blit(textSurfaceObj, textRectObj)

            fontObj = pygame.font.Font('freesansbold.ttf', 40)
            textSurfaceObj = fontObj.render('Средняя скорость: {} км/ч'.format(KPI[1]), True, Color("#FFFF00"), Color("#0000FF"))
            textRectObj = textSurfaceObj.get_rect()
            textRectObj.center = (350, DISPLAY[1]-30)
            screen.blit(textSurfaceObj, textRectObj)

            pygame.display.update()  # обновление и вывод всех изменений на экран

        # Count KPI
        max_time = max([stop.no_bus_time for stop in stops])
        speed = np.mean([bus.speed / 0.27 for bus in buses if bus.can_go])
        if speed != speed:
            speed = 0
        else:
            speed = int(round(speed))
        KPI = [max_time, speed]

        TIME = (TIME + PERIOD)%(3600*24*7)
        GLOBAL_TIME += PERIOD

        print(get_hour())

        #time.sleep(PERIOD/2)
        #print(TIME)
