import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import random
import _thread
from environment import Environment, simple_bot_logic

hour = 0
day = 0
bus_count = 0
simulation_speed = 1
exit = False
env = Environment(True)

class ControlPanel(QMainWindow):
	def __init__(self, parent=None):
		super(ControlPanel, self).__init__(parent)

		uic.loadUi('demo.ui', self)
		self.day_slider.valueChanged.connect(self.day_changed)
		self.time_slider.valueChanged.connect(self.hour_changed)
		self.speed_slider.valueChanged.connect(self.speed_changed)
		self.add_bus_btn.clicked.connect(self.add_bus)
		self.del_bus_btn.clicked.connect(self.del_bus)
		self.remove_repairs_btn.clicked.connect(self.remove_repairs)
		self.speeds_checkBox.stateChanged.connect(self.display_speeds)

	def display_speeds(self, a):
		env.display_speeds(a)

	def remove_repairs(self):
		env.remove_road_repairs()

	def day_changed(self, a):
		env.set_week_day(a)

	def hour_changed(self, a):
		env.set_hour(a)

	def setInfo(self):
		self.day_slider.setValue(day)
		self.time_slider.setValue(hour)
		self.bus_count_label.setText(str(bus_count))

	def add_bus(self):
		env.add_bus()

	def del_bus(self):
		env.del_bus()

	def speed_changed(self, a):
		global simulation_speed
		simulation_speed = a


def pyqt_app():
	global exit
	app = QtWidgets.QApplication(sys.argv)
	MainWindow = ControlPanel()

	timer = QTimer()
	timer.timeout.connect(MainWindow.setInfo)
	timer.start(50)

	MainWindow.show()
	app.exec_()
	exit = True
	sys.exit()

import numpy as np

def get_info():
	global hour, day, bus_count
	hour, day, bus_count = env.get_hour(), env.get_weekday(), env.get_bus_count()

get_info()
_thread.start_new_thread ( pyqt_app, () )

buses_data = []
KPI_data = []
stops_data = []
def collect_data():
	buses_data.append([[i.max_speed, i.speed, env.TIME] for i in env.buses
					   if i.wanted_action and (i.decision == 1 or i.decision == 2)])
	KPI_data.append((env.KPI, env.TIME))
	#stops_data.append([ (i.no_bus_time, env.TIME) for i in env.stops ])

it = 0
features = env.reset()
while True:
	get_info()
	features, a, a, a = env.step(list(map(simple_bot_logic, features)))

	if it % simulation_speed == 0:
		env.render()
	it = (it + 1)%10
	'''collect_data()
	if it > 3600*24*7//4:
		break
	it += 1'''
	if exit:
		break

for i in env.stops:
	stops_data.append(i.wait_times)

np.save("graphs/stops_data2.npy", stops_data)
np.save("graphs/buses_data2.npy", buses_data)