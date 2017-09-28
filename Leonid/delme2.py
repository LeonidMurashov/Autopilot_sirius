import _thread



import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QSlider
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import random

rar = 0

class App(QMainWindow):
	def __init__(self):
		super().__init__()
		self.title = 'Управление средой'
		self.left = 10
		self.top = 10
		self.width = 400
		self.height = 140
		self.initUI()

	def initUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		# Create textbox
		self.slider = QSlider(Qt.Horizontal, self)
		self.slider.move(20, 80)
		self.slider.move

		self.show()

	@pyqtSlot()
	def on_click(self):


def pyqt_app():
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())


_thread.start_new_thread ( pyqt_app, () )

while True:
	print(rar)