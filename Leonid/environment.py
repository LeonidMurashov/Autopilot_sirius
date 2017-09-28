import random
import pandas as pd
import time
from math import cos, sin, pi
import numpy as np
from drawer import Drawer
from collections import deque
from joblib import Parallel, delayed

LENGTH = 15600
PERIOD = 4
BUSES_COUNT = 15
BUSES_CARET = 5
clockwise = True
iterator = 0
simple_bot_model = None
rage_mode = False
p = [3, 15]

jams_file = "data_files/jams_test.npy"
df_lights = pd.read_csv("data_files/street_lights_converted.csv")
df_stops = pd.read_csv("data_files/stops_converted.csv")
road = np.load(jams_file)

def load_simple_bot(model, weights_path):
	global simple_bot_model
	simple_bot_model = model
	simple_bot_model.load_weights(weights_path)

def get_distance(a, b):
	return min(abs(b - a), LENGTH - abs(b - a))

def add_road_repair(z):
	x1 = int(z / LENGTH * len(road))%len(road)
	x2 = int((z + 500 * ( 1 if clockwise else -1 )) / LENGTH * len(road))%len(road)
	for index in range(x1, x2):
		for week_day in range(len(road[index])):
			for hour in range(len(road[index][week_day])):
				road[index][week_day][hour] = 7

def reset_traffic():
	global road
	road = np.load(jams_file)

# Look at traffic jams
def get_speed(coordinate, week_day, hour):
	index = int(coordinate / LENGTH * len(road))%len(road)  # TODO check it
	speed = road[index][week_day][hour]
	#if speed != None and (speed > 60 or speed < 3):
	#	print("bad speed", speed)
	return speed if speed == speed and speed != None else 50

def simple_bot_logic(features):
	global simple_bot_model
	if simple_bot_model == None:
		interval_forward = features[0]
		interval_backward = features[1]
		speed = features[2]
		max_speed = features[3]
		distances = features[4]
		#print(features)
		#if distances < 500:
		#	if speed/0.27 < 5:
		#		return 0
		#	return 1

		if random.randint(0,p[0]) == 0:
			return 0

		if not rage_mode and ((max_speed - speed)/0.27 > 10 or speed/0.27 < 15):
			return 0

		if abs(interval_backward - interval_forward) > p[1]:
			if interval_forward > interval_backward:
				return 0
			else:
				if speed/0.27 < 8:
					return 1
				else:
					return 2
		else:
			return 1


	else:
		state = np.reshape(features, [1, len(features)])
		act_values = simple_bot_model.predict(state)
		return np.argmax(act_values[0])  # returns action

def run_bot_logic(features):
	return 0

class Light:
	def __init__(self, red, green, coordinate, now):  # 0-10 red and 11-20 green
		self.red = red
		self.green = green
		self.iterator = now#random.randint(0, red + green - 1)
		self.coordinate = coordinate
		self.next = 0

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
		self.next = 0
		self.wait_times = []

	def add_bus(self, bus, want_wait, env):
		self.bus_stack.append(bus)
		if len(self.bus_stack) == 1:
			self.wait_times.append([self.no_bus_time, env.TIME])
			if want_wait:
				self.with_bus_time = max(10 * 60,
									 15 if self.no_bus_time < 8 * 60 else 15 + (self.no_bus_time - 8 * 60) / 20)
			else:
				self.with_bus_time = min(5 * 60,
										 15 if self.no_bus_time < 8 * 60 else 15 + (self.no_bus_time - 8 * 60) / 20)	
		self.no_bus_time = 0

	def can_go(self, bus):
		return (not bus in self.bus_stack)  # or\
		# self.bus_stack.index(bus) >= 3

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
	def __init__(self, coordinate, get_prev_stop, get_prev_light, get_hour, get_weekday):
		self.coordinate = coordinate
		self.get_prev_stop = get_prev_stop
		self.get_prev_light = get_prev_light
		self.get_hour = get_hour
		self.get_weekday = get_weekday

		self.last_stop = get_prev_stop(coordinate)
		self.last_light = get_prev_light(coordinate)
		self.stop_time = 0
		self.can_go = True
		self.speed = 0
		self.decision = 0
		self.interval_forward = 0
		self.interval_backward = 0
		self.chosen_one = False
		self.wanted_action = False

	def calculate_interval(self, prev, next):
		dist1 = LENGTH - prev + self.coordinate if self.coordinate < prev else self.coordinate - prev
		dist2 = LENGTH - self.coordinate + next if self.coordinate > next else next - self.coordinate
		dist = [dist1, dist2]
		dist.append(get_speed(prev, self.get_weekday(), (self.get_hour()+1)%24))	# TODO do it normal way
		dist.append(get_speed(next, self.get_weekday(), (self.get_hour()+1)%24)) 	# TODO do it normal way
		time = [int(dist[0] / dist[2]), int(dist[1] / dist[3])]
		self.interval_forward = time[0] 
		self.interval_backward = time[1]

	def step(self, prev, next, env):
		self.calculate_interval(prev, next)
		if self.stop_time != 0:
			self.stop_time = max(0, self.stop_time - PERIOD)
			return
		if not self.last_stop.can_go(self):
			self.can_go = False
			self.speed = 0
			return

		prev_stop = self.get_prev_stop(self.coordinate)
		prev_light = self.get_prev_light(self.coordinate)

		# Check if we stay at street light
		if prev_light != self.last_light:
			if not prev_light.can_go():
				self.can_go = False
				self.speed = 0
				return
			else:
				self.last_light = prev_light
		self.can_go = True

		self.wanted_action = True

		self.max_speed = get_speed(self.coordinate, self.get_weekday(), self.get_hour()) * 0.27
		brake_dist = 3 / 2 * (self.speed) ** 2 / 1.2
		# Check if we need accel or stop
		dist_next = get_distance(prev_stop.next.coordinate, self.coordinate)
		if dist_next < brake_dist:  # FIX ME
			accel = -1.2
			self.wanted_action = False
		else:
			# Agent policy
			if self.decision == 0:
				accel = 1.3
			elif self.decision == 2:
				accel = -1.2
			else:
				accel = 0


		if self.speed + accel * PERIOD > self.max_speed:
			self.speed = self.max_speed
		else:
			self.speed += accel * PERIOD

		if self.speed < 0:
			self.speed = 0

		self.coordinate = (self.coordinate + self.speed * PERIOD * ( -1 if clockwise else 1)) % LENGTH
		if prev_stop != self.last_stop:
			self.last_stop = prev_stop
			prev_stop.add_bus(self, self.interval_backward > 10*60, env)
	def get_features(self, buses_around):
		features = []
		features.append([self.interval_forward, self.interval_backward, self.speed, self.max_speed])

		'''if clockwise:
			features.append([ get_distance(buses_around[BUSES_CARET].coordinate, buses_around[BUSES_CARET - 1].coordinate) +
							  get_distance(buses_around[BUSES_CARET - 1].coordinate, buses_around[BUSES_CARET - 2].coordinate)])
		else:
			features.append([ get_distance(buses_around[BUSES_CARET].coordinate, buses_around[BUSES_CARET + 1].coordinate) +
							  get_distance(buses_around[BUSES_CARET + 1].coordinate, buses_around[BUSES_CARET + 2].coordinate)])'''

		features.append([get_distance(buses_around[BUSES_CARET].coordinate, buses_around[BUSES_CARET - 1].coordinate)])


		# Time intervals
		features.append([bus.interval_forward for bus in buses_around])
		# Self speed
		features.append([bus.speed for bus in buses_around])
		# Traffic
		features.append([bus.max_speed for bus in buses_around])
		# Distances
		features.append([ get_distance(buses_around[i+1].coordinate, buses_around[i].coordinate)
						  for i in range(len(buses_around)-1)])
		# Next stops
		features.append([min(get_distance(bus.last_light.next.coordinate, bus.coordinate), get_distance(bus.last_stop.next.coordinate, bus.coordinate)) for bus in buses_around])
		# Hour, week_day
		features.append([self.get_hour(), self.get_weekday()])
		return np.concatenate(features).ravel()

class Environment:
	actions = [0,1,2]
	prev_reward = 0

	def __init__(self, visualization):
		global road
		self.lights = []; self.stops = [];	self.buses = []
		self.TIME = random.randint(0,7*24*3600)
		self.GLOBAL_TIME = 0
		self.KPI = [0, 0]
		self.KPI_ALL = []
		self.reward_history = deque(maxlen=1800)
		self.speed_history = deque(maxlen=100)
		self.wait_history = deque(maxlen=100)
		if visualization:
			self.drawer = Drawer()

		for _, i in df_lights.iterrows():
			self.lights.append(Light(i["red"], i["green"], i["dot"], i["now"]))
			self.lights = sorted(self.lights, key=lambda x: x.coordinate)
		for _, i in df_stops.iterrows():
			self.stops.append(Stop(i["dot"]))

		self.lights = sorted(self.lights, key=lambda x: x.coordinate)
		for i in range(len(self.lights)):
			self.lights[i].next = self.lights[((i - 1) if clockwise else (i + 1)) % len(self.lights)]
			self.lights[i].prev = self.lights[((i + 1) if clockwise else (i - 1)) % len(self.lights)]

		self.stops = sorted(self.stops, key=lambda x: x.coordinate)
		for i in range(len(self.stops)):
			self.stops[i].next = self.stops[((i - 1) if clockwise else (i + 1)) % len(self.stops)]
			self.stops[i].prev = self.stops[((i + 1) if clockwise else (i - 1)) % len(self.stops)]

		self.buses = [Bus(random.randint(0, LENGTH-1), self.get_prev_stop, self.get_prev_light, self.get_hour, self.get_weekday) for i in range(BUSES_COUNT)]
		# buses = [Bus(random.randint(0, LENGTH-1)) for i in range(0, BUSES_COUNT*100, 100)]

	def get_buses_around(self, bus):
		index = self.buses.index(bus)
		arr = []
		for i in range(index - BUSES_CARET, index + BUSES_CARET + 1):
			arr.append(self.buses[(i) % len(self.buses)])
		return arr

	def set_hour(self, a):
		self.TIME = self.TIME - self.TIME//3600%24*3600 + a*3600

	def get_hour(self):
		return int((self.TIME - int(self.TIME / (3600 * 24)) * 24 * 3600 - self.TIME % 3600) / 3600)

	def set_week_day(self, a):
		self.TIME = self.TIME - self.TIME//(3600*24)*3600*24 + a*3600*24

	def get_weekday(self):
		return int(self.TIME / (3600 * 24))

	def add_bus(self):
		global BUSES_COUNT
		BUSES_COUNT += 1

	def del_bus(self):
		global BUSES_COUNT
		if BUSES_COUNT != 0:
			BUSES_COUNT -= 1

	def get_bus_count(self):
		return len(self.buses)

	def remove_road_repairs(self):
		if len(self.drawer.road_repair) != 0:
			self.drawer.road_repair = []
			reset_traffic()

	def display_speeds(self, display):
		self.drawer.display_speeds = display

	def reward_function(self):
		if self.KPI[1] == 0:
			self.KPI[1] = 0.0001
		#return self.KPI[1] / 50 + 3600 / self.KPI[0] * 4
		self.reward_history.append(36000000/self.KPI[0])
		return np.ma.average(self.reward_history)

	def get_prev_stop(self, coordinate):
		for stop in self.stops[::-1]:
			if stop.coordinate < coordinate:
				return stop.prev if clockwise else stop
		if len(self.stops) > 0:
			return self.stops[len(self.stops) - 1].prev if clockwise else self.stops[len(self.stops) - 1]
		return None

	def get_prev_light(self, coordinate):
		for light in self.lights[::-1]:
			if light.coordinate < coordinate:
				return light.prev if clockwise else light
		if len(self.lights) > 0:
			return self.lights[len(self.lights) - 1].prev if clockwise else self.lights[len(self.lights) - 1]
		else:
			return None

	def render(self):
		self.drawer.render(self, get_speed, add_road_repair, self.get_hour(), self.get_weekday(), int(self.TIME % 3600 // 60), self.KPI)

	def stabilize(self, features):
		for i in range(300):
			actions = []
			for i in features:
				actions.append(simple_bot_logic(i))
			features, rew, _, _ = self.step(actions)
			self.KPI_ALL.append(self.KPI[0])
		self.reward_history.clear()
		return features

	def reset(self):
		self.TIME = 4*24*3600+18*3600#random.randint(0,7*24*3600-1)
		self.buses.clear()
		self.buses = [Bus(random.randint(0, LENGTH-1), self.get_prev_stop, self.get_prev_light, self.get_hour, self.get_weekday) for i in range(BUSES_COUNT)]
		self.buses[0].chosen_one = True

		self.do_step()
		environment = [bus.get_features(self.get_buses_around(bus)) for bus in self.buses]
		self.prev_reward = self.reward_function()
		return self.stabilize(environment)# TODO REMOVE IF NOT CHOSEN ONE

	def do_step(self):
		global rage_mode
		for light in self.lights:
			light.step()
		for stop in self.stops:
			stop.step()
		# {% yaroslav %}
		self.buses = sorted(self.buses, key=lambda x: x.coordinate)
		for i in range(0, len(self.buses)):
			self.buses[i].step(self.buses[(i - 1) % len(self.buses)].coordinate, self.buses[(i + 1) % len(self.buses)].coordinate, self)
		# {% end yaroslav %}

		# Count KPI
		max_time = max([stop.no_bus_time for stop in self.stops])
		speed = np.mean([bus.speed / 0.27 for bus in self.buses if bus.can_go])
		if speed != speed:
			speed = 0
		else:
			speed = int(round(speed))
		self.speed_history.append(speed)
		self.wait_history.append(max_time)
		self.KPI = [int(np.ma.average(self.wait_history)), int(np.ma.average(self.speed_history))]

		if self.KPI[0] > 15*60:
			rage_mode = True
		else:
			rage_mode = False
		self.TIME = (self.TIME + PERIOD) % (3600 * 24 * 7)
		self.GLOBAL_TIME += PERIOD

		#DELME
		#print(max([i.interval_backward for i in self.buses]))

	def find_chosen_one(self):
		for i in range(len(self.buses)):
			if self.buses[i].chosen_one:
				return i

	# Step for chosen one model
	def step2(self, action):
		global iterator

		self.buses[self.find_chosen_one()].decision = action
		self.do_step()

		# if iterator % 1000 == 0:
		# 	print("KPI:", self.KPI)
		iterator += 1

		environment = [bus.get_features(self.get_buses_around(bus)) for bus in self.buses]
		chosen_one = self.find_chosen_one()

		for i in range(0,len(environment)):
			if i != chosen_one:
				self.buses[i].decision = simple_bot_logic(environment[i])

		'''decisions = Parallel(n_jobs=-1, verbose=0, backend="threading")(
			map(delayed(simple_bot_logic), environment))
		for i in range(len(decisions)):
			if i != chosen_one:
				self.buses[i].decision = decisions[i]'''

		# Count reward
		rew = self.reward_function()
		delta = rew - self.prev_reward
		self.prev_reward = rew

		return environment[chosen_one], delta, iterator % 10000 == 0, False

	def step(self, action):
		global iterator
		
		for i in range(len(action)):
			self.buses[i].decision = action[i]

		# Delete/add buses here
		if len(self.buses) < BUSES_COUNT:
			self.buses.append(Bus(random.randint(0, LENGTH - 1), self.get_prev_stop, self.get_prev_light, self.get_hour,
								  self.get_weekday))
		elif len(self.buses) > BUSES_COUNT:
			del self.buses[random.randint(0, len(self.buses) - 1)]
		self.do_step()

		#print(iterator)
		# if (iterator-1) % 1000 == 0:
		# 	print("MEAN KPI:", np.mean(self.KPI_ALL))
		iterator += 1

		environment = [bus.get_features(self.get_buses_around(bus)) for bus in self.buses]

		rew = self.reward_function()
		delta = rew - self.prev_reward
		self.prev_reward = rew

		return environment, delta, iterator % 10000 == 0, False