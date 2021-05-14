#!/usr/bin/python3

import socket, time, requests, datetime, os, sys, json
from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic

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
		"host": "127.0.0.1",
		"port": 4532
	}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		uic.loadUi(self.relpath("main.ui"), self)
		self.settingsbutton.clicked.connect(self.settingspressed)

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
			f = open(home+"/.cloudlogpycat.json", "rt")
			self.settings_dict = json.loads(f.read())
		else:
			f = open(home+"/.cloudlogpycat.json", "wt")
			f.write(json.dumps(self.settings_dict))
		#connect the change events to resave messages 
		#.textChanged.connect(self.savestuff)

	def savestuff(self):
		"""
		save state as a json file in the home directory
		"""
		home = os.path.expanduser("~")
		f = open(home+"/.cloudlogpycat.json", "wt")
		f.write(json.dumps(self.settings_dict))

	def settingspressed(self):
		settingsdialog = settings(self)
		settingsdialog.exec()
		self.loadsaved()


	def rigconnect(self):
		try:
			radiosocket=socket.socket()
			radiosocket.settimeout(0.1)
			radiosocket.connect((self.settings_dict['host'], int(self.settings_dict['port'])))
			radiosocket.send(b'f\n')
			self.newfreq = radiosocket.recv(1024).decode().strip()
			radiosocket.send(b'm\n')
			self.newmode = radiosocket.recv(1024).decode().strip().split()[0]
			radiosocket.close()
			self.errorline_label.setText("")
		except:
			self.errorline_label.setText(f"Unable to connect to: {str(self.settings_dict['host'])}:{str(self.settings_dict['port'])}")

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
			f = open(home+"/.cloudlogpycat.json", "rt")
			self.settings_dict = json.loads(f.read())
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
		f = open(home+"/.cloudlogpycat.json", "wt")
		f.write(json.dumps(self.settings_dict))
		
	
app = QtWidgets.QApplication(sys.argv)
app.setStyle('Fusion')
window = MainWindow()
window.show()
window.loadsaved()
#window.rigconnect()
timer = QtCore.QTimer()
timer.timeout.connect(window.mainloop)
timer.start(1000)
app.exec()
