# Non-linearity
import pickle
from math import pi, cos, sin, atan2
import pygame
from pygame import *
import pygame.gfxdraw as gf

# Pygame consts
DISPLAY = (1000, 700)  # Группируем ширину и высоту в одну переменную
c = (500, 400)
r = 212
LENGTH = 15600
BACKGROUND_COLOR = "#555555"
PLATFORM_COLOR = "#555555"
BUS_COLOR = "#0000FF"
GREEN = (0,255,0)
RED = (255,0,0)

DAY = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
background = pygame.image.load("pictures/moscow_main.jpg")
BUS_DIM = (25,25)
LIGHT_DIM = (30,30)
ROAD_REPAIR_DIM = (30,30)
road_repair_image = pygame.transform.scale(pygame.image.load("pictures/road_repair.gif"), ROAD_REPAIR_DIM)
bus_image = pygame.transform.scale(pygame.image.load("pictures/AWT-Bus.png"), BUS_DIM)
light_image = [pygame.transform.scale(pygame.image.load("pictures/green.png"), LIGHT_DIM),
		 pygame.transform.scale(pygame.image.load("pictures/red.png"), LIGHT_DIM)]

DISPLAY_ACTION = True  # True
DISPLAY_TRAFFIC = True

with open('ring_shape/ring_function.pickle', 'rb') as f:
	function = pickle.load(f)
def coordinate_to_circle(z, width, offset=0, height=-1):
	if height == -1:
		height = width
	z = z / LENGTH * 2 * pi
	non_linearity = function(((z)) % (2 * pi) - pi)  # get_nonlinearity((z/2/pi)*c)  *(TIME/60)
	return (cos(-z) * (r + offset) * non_linearity + c[0] - width / 2,
			sin(-z) * (r + offset) * non_linearity + c[1] - height / 2)

def draw_rect(screen, z, size, color, offset=0):
	pf = Surface((size, size))
	pf.fill(color)
	screen.blit(pf, coordinate_to_circle(z, size, offset))

class Drawer:
	def __init__(self):
		pygame.init()
		pygame.display.set_caption("Super MGT Boy")
		self.bg = Surface(DISPLAY)
		self.road_repair = []
		self.screen = pygame.display.set_mode(DISPLAY)
		self.display_speeds = False


	def render(self, env, get_speed,add_road_repair , hour, week_day, minute, KPI):
		buses = env.buses; lights = env.lights; stops = env.stops

		for e in pygame.event.get():  # Обрабатываем события
			if e.type == pygame.MOUSEBUTTONDOWN:
				# Add traffic jam
				x, y = pygame.mouse.get_pos()
				z = LENGTH - ((-atan2(-(y-c[1]), x-c[0]))/(2*pi)*LENGTH)%LENGTH
				non_linearity = function(((z)) % (2 * pi) - pi)
				#if (r - 50)*non_linearity < (x**2 + y**2)**0.5 < (r + 50)*non_linearity:
				add_road_repair(z)
				self.road_repair.append(z)

			if e.type == QUIT:
				raise (SystemExit, "QUIT")

		# screen.blit(bg, (0, 0))
		self.screen.blit(background, (-339, -50))  # Каждую грёбаную итерацию необходимо всё перерисовывать

		if DISPLAY_TRAFFIC:
			for i in range(0, LENGTH, 30):
				draw_rect(self.screen, i, 7, pygame.Color(50, 50, 50))

			for i in range(0, LENGTH, 30):
				speed = get_speed(i, week_day, hour)
				color = pygame.Color(255, 0, 0) if speed < 17 else (
					pygame.Color(0, 150, 0) if speed > 33 else pygame.Color(245, 245, 0))
				draw_rect(self.screen, i, 5, color)

		for repair in self.road_repair:
			self.screen.blit(road_repair_image, coordinate_to_circle(repair, width=ROAD_REPAIR_DIM[0], height=ROAD_REPAIR_DIM[1]))

		#DELME
		fontObj = pygame.font.Font('freesansbold.ttf', 15)

		for bus in buses:
			coordinates = coordinate_to_circle(bus.coordinate, width=BUS_DIM[0], height=BUS_DIM[1])

			if self.display_speeds:
				textSurfaceObj = fontObj.render('{}'.format(int(bus.speed/0.27)), True, Color("#FFFF00"),
												Color("#0000FF"))
				textRectObj = textSurfaceObj.get_rect()
				textRectObj.center = coordinates
				self.screen.blit(textSurfaceObj, textRectObj)

			self.screen.blit(bus_image, coordinates)

		for light in lights:
			sf = Surface((LIGHT_DIM[0],LIGHT_DIM[1]))
			color = GREEN if light.can_go() else RED
			gf.aacircle(sf, LIGHT_DIM[0]//2, LIGHT_DIM[1]//2, LIGHT_DIM[0]//3, color)
			gf.filled_circle(sf, LIGHT_DIM[0]//2, LIGHT_DIM[1]//2, LIGHT_DIM[0]//3, color)
			self.screen.blit(sf, coordinate_to_circle(light.coordinate, 20, 40))
			#self.screen.blit(light_image[0 if light.can_go() else 1], coordinate_to_circle(light.coordinate, width=BUS_DIM[0], height=BUS_DIM[1], offset=30))

		for stop in stops:
			no_bus = stop.no_bus_time if stop.no_bus_time != 0 else 0.01
			color = pygame.Color(max(int(min(255, no_bus / 600 * 255)), 0),
								 max(int(min(255, 255 * 60 / no_bus * 1)), 0), 0)
			draw_rect(self.screen, stop.coordinate, 8, color, -30)

		font_size = 40

		# Get and display KPI
		fontObj = pygame.font.Font('freesansbold.ttf', font_size)
		textSurfaceObj = fontObj.render('Ожидание: {} мин.'.format(round(KPI[0]//60)), True, Color("#FFFF00"),
										Color("#0000FF"))
		textRectObj = textSurfaceObj.get_rect()
		textRectObj.center = ((textRectObj[2] - textRectObj[0])//2+2, (textRectObj[3]-textRectObj[1])//2+2)
		self.screen.blit(textSurfaceObj, textRectObj)

		fontObj = pygame.font.Font('freesansbold.ttf', font_size)
		textSurfaceObj = fontObj.render(
			'{}:{} {}'.format(hour, minute, DAY[week_day]), True, Color("#FFFF00"),
			Color("#0000FF"))
		textRectObj = textSurfaceObj.get_rect()
		textRectObj.center = (DISPLAY[0] - 200, 30)
		self.screen.blit(textSurfaceObj, textRectObj)

		fontObj = pygame.font.Font('freesansbold.ttf', font_size)
		textSurfaceObj = fontObj.render('Средняя скорость: {} км/ч'.format(KPI[1]), True, Color("#FFFF00"),
										Color("#0000FF"))
		textRectObj = textSurfaceObj.get_rect()
		textRectObj.center = ((textRectObj[2] - textRectObj[0])//2+2, (textRectObj[3]-textRectObj[1])//2*3+4)
		self.screen.blit(textSurfaceObj, textRectObj)

		pygame.display.update()  # обновление и вывод всех изменений на экран
