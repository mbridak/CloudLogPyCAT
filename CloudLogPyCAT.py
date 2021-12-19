#!/usr/bin/python3

import logging
logging.basicConfig(level=logging.WARNING)

import xmlrpc.client
import requests, datetime, os, sys
from json import dumps, loads
from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QFontDatabase

def relpath(filename):
		try:
			base_path = sys._MEIPASS # pylint: disable=no-member
		except:
			base_path = os.path.abspath(".")
		return os.path.join(base_path, filename)

def load_fonts_from_dir(directory):
		families = set()
		for fi in QDir(directory).entryInfoList(["*.ttf", "*.woff", "*.woff2"]):
			_id = QFontDatabase.addApplicationFont(fi.absoluteFilePath())
			families |= set(QFontDatabase.applicationFontFamilies(_id))
		return families

class MainWindow(QtWidgets.QMainWindow):
	oldfreq = '0'
	oldmode = 'none'
	newfreq = '0'
	newmode = 'none'
	s=False
	settings_dict ={
		"key": "yourAPIkey",
		"cloudurl": "http://www.youraddress.com/index.php/api/radio",
		"radio_name": "IC-7300",
		"host": "localhost",
		"port": 12345
	}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		uic.loadUi(self.relpath("main.ui"), self)
		self.settingsbutton.clicked.connect(self.settingspressed)
		self.server = xmlrpc.client.ServerProxy(f"http://{self.settings_dict['host']}:{self.settings_dict['port']}")

	def relpath(self, filename):
		"""
		lets the program know where the temp execution location is.
		"""
		try:
			base_path = sys._MEIPASS # pylint: disable=no-member
		except:
			base_path = os.path.abspath(".")
		return os.path.join(base_path, filename)

	def loadsaved(self):
		"""
		load saved defaults if they exist.
		otherwise write some sane defaults as a json text file in the users home directory. 
		"""
		home = os.path.expanduser("~")
		if os.path.exists(home+"/.cloudlogpycat.json"):
			with open(home+"/.cloudlogpycat.json", "rt") as f:
				self.settings_dict = loads(f.read())
		else:
			with open(home+"/.cloudlogpycat.json", "wt") as f:
				f.write(dumps(self.settings_dict))
		self.server = xmlrpc.client.ServerProxy(f"http://{self.settings_dict['host']}:{self.settings_dict['port']}")

	def savestuff(self):
		"""
		save state as a json file in the home directory
		"""
		home = os.path.expanduser("~")
		with open(home+"/.cloudlogpycat.json", "wt") as f:
			f.write(dumps(self.settings_dict))

	def settingspressed(self):
		settingsdialog = settings(self)
		settingsdialog.exec()
		self.loadsaved()


	def rigconnect(self):
		try:
			self.newfreq = self.server.rig.get_vfo()
			self.newmode = self.server.rig.get_mode()
			self.errorline_label.setText("")
		except Exception as e:
			self.errorline_label.setText(f"{e}")

	def mainloop(self):
		self.rigconnect()

		if self.newfreq != self.oldfreq or self.newmode != self.oldmode:
			self.freq_label.setText(self.newfreq)
			self.mode_label.setText(self.newmode)
			ts=datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M")
			payload = {'key':self.settings_dict["key"],'radio':self.settings_dict["radio_name"],'frequency':self.newfreq,'mode':self.newmode,'timestamp':ts}
			r = requests.post(self.settings_dict['cloudurl'], json=payload)
			self.response_label.setText(str(r.status_code))
			self.oldfreq = self.newfreq
			self.oldmode = self.newmode

class settings(QtWidgets.QDialog):
	settings_dict = {}
	def __init__(self, parent=None):
		super().__init__(parent)
		uic.loadUi(self.relpath("settings.ui"), self)
		self.buttonBox.accepted.connect(self.saveChanges)
		self.loadsettings()

	def relpath(self, filename):
		"""
		lets the program know where the temp execution location is.
		"""
		try:
			base_path = sys._MEIPASS # pylint: disable=no-member
		except:
			base_path = os.path.abspath(".")
		return os.path.join(base_path, filename)

	def loadsettings(self):
		home = os.path.expanduser("~")
		if os.path.exists(home+"/.cloudlogpycat.json"):
			with open(home+"/.cloudlogpycat.json", "rt") as f:
				self.settings_dict = loads(f.read())
			self.radioname_field.setText(self.settings_dict['radio_name'])
			self.cloudlogapi_field.setText(self.settings_dict['key'])
			self.cloudlogurl_field.setText(self.settings_dict['cloudurl'])
			self.rigcontrolip_field.setText(self.settings_dict['host'])
			self.rigcontrolport_field.setText(str(self.settings_dict['port']))

	def saveChanges(self):
		self.settings_dict['radio_name'] = self.radioname_field.text()
		self.settings_dict['key'] = self.cloudlogapi_field.text()
		self.settings_dict['cloudurl'] =self.cloudlogurl_field.text()
		self.settings_dict['host'] = self.rigcontrolip_field.text()
		self.settings_dict['port'] = int(self.rigcontrolport_field.text())
		home = os.path.expanduser("~")
		with open(home+"/.cloudlogpycat.json", "wt") as f:
			f.write(dumps(self.settings_dict))
		
	
app = QtWidgets.QApplication(sys.argv)
app.setStyle('Fusion')
font_dir = relpath("font")
families = load_fonts_from_dir(os.fspath(font_dir))
logging.info(families)
window = MainWindow()
window.show()
window.loadsaved()
#window.rigconnect()
timer = QtCore.QTimer()
timer.timeout.connect(window.mainloop)
timer.start(1000)
app.exec()
