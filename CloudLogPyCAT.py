#!/usr/bin/python3
"""
CloudLogPyCAT

Small app that monitors you radio via CAT and updates Cloudlog to assist logging.

Who's responsible: Michael Bridak K6GTE
Where to yell at : michael.bridak@gmail.com
"""

# pylint: disable=no-name-in-module
# pylint: disable=c-extension-no-member
# pylint: disable=invalid-name

import logging
import datetime
import os
import sys
from json import dumps, loads
import requests
from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QFontDatabase
from cat_interface import CAT

logging.basicConfig(level=logging.WARNING)


def relpath(filename):
    """Checks to see if program has been packaged with pyinstaller.
    If so base dir is in a temp folder.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = getattr(sys, "_MEIPASS")
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, filename)


def load_fonts_from_dir(directory):
    """loads available font families"""
    _families = set()
    for filename in QDir(directory).entryInfoList(["*.ttf", "*.woff", "*.woff2"]):
        _id = QFontDatabase.addApplicationFont(filename.absoluteFilePath())
        _families |= set(QFontDatabase.applicationFontFamilies(_id))
    return _families


class MainWindow(QtWidgets.QMainWindow):
    """Yep, it's the main window class."""

    oldfreq = "0"
    oldmode = "none"
    newfreq = "0"
    newmode = "none"
    s = False
    settings_dict = {
        "key": "yourAPIkey",
        "cloudurl": "http://www.youraddress.com/index.php/api/radio",
        "radio_name": "IC-7300",
        "CAT_type": "rigctld",
        "host": "localhost",
        "port": 4532,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(self.relpath("main.ui"), self)
        self.settingsbutton.clicked.connect(self.settingspressed)
        self.cat_interface = None

    def relpath(self, filename):
        """Checks to see if program has been packaged with pyinstaller.
        If so base dir is in a temp folder.
        """
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base_path = getattr(sys, "_MEIPASS")
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, filename)

    def loadsaved(self):
        """
        load saved defaults if they exist.
        otherwise write some sane defaults as a json text file in the users home directory.
        """
        home = os.path.expanduser("~")
        if os.path.exists(home + "/.cloudlogpycat.json"):
            with open(
                home + "/.cloudlogpycat.json", "rt", encoding="utf-8"
            ) as file_handle:
                self.settings_dict = loads(file_handle.read())
        else:
            with open(
                home + "/.cloudlogpycat.json", "wt", encoding="utf-8"
            ) as file_handle:
                file_handle.write(dumps(self.settings_dict))
        self.cat_interface = CAT(
            self.settings_dict["CAT_type"],
            self.settings_dict["host"],
            self.settings_dict["port"],
        )

    def savestuff(self):
        """
        save state as a json file in the home directory
        """
        home = os.path.expanduser("~")
        with open(home + "/.cloudlogpycat.json", "wt", encoding="utf-8") as file_handle:
            file_handle.write(dumps(self.settings_dict))

    def settingspressed(self):
        """Creates/Calls the settings window."""
        settingsdialog = Settings(self)
        settingsdialog.exec()
        self.loadsaved()

    def rigconnect(self):
        """get the radio state."""
        try:
            self.newfreq = self.cat_interface.get_vfo()
            self.newmode = self.cat_interface.get_mode()
        except Exception:
            pass

    def mainloop(self):
        """Where the magik happens"""
        self.rigconnect()
        if self.newfreq != self.oldfreq or self.newmode != self.oldmode:
            self.freq_label.setText(self.newfreq)
            self.mode_label.setText(self.newmode)
            time_stamp = datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M")
            payload = {
                "key": self.settings_dict["key"],
                "radio": self.settings_dict["radio_name"],
                "frequency": self.newfreq,
                "mode": self.newmode,
                "timestamp": time_stamp,
            }
            response = requests.post(self.settings_dict["cloudurl"], json=payload)
            self.response_label.setText(str(response.status_code))
            self.oldfreq = self.newfreq
            self.oldmode = self.newmode


class Settings(QtWidgets.QDialog):
    """Class to handle... Yep, the settings."""

    settings_dict = {}

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(self.relpath("settings.ui"), self)
        self.buttonBox.accepted.connect(self.save_changes)
        self.loadsettings()

    def relpath(self, filename):
        """Checks to see if program has been packaged with pyinstaller.
        If so base dir is in a temp folder.
        """
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base_path = getattr(sys, "_MEIPASS")
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, filename)

    def loadsettings(self):
        """Loads settings from JSON file."""
        home = os.path.expanduser("~")
        if os.path.exists(home + "/.cloudlogpycat.json"):
            with open(
                home + "/.cloudlogpycat.json", "rt", encoding="utf-8"
            ) as file_handle:
                self.settings_dict = loads(file_handle.read())
            self.radioname_field.setText(self.settings_dict["radio_name"])
            self.cloudlogapi_field.setText(self.settings_dict["key"])
            self.cloudlogurl_field.setText(self.settings_dict["cloudurl"])
            if (
                "CAT_type" in self.settings_dict
                and self.settings_dict["CAT_type"] == "rigctld"
            ):
                self.rigctld_radioButton.setChecked(True)
            if (
                "CAT_type" in self.settings_dict
                and self.settings_dict["CAT_type"] == "flrig"
            ):
                self.flrig_radioButton.setChecked(True)
            self.rigcontrolip_field.setText(self.settings_dict["host"])
            self.rigcontrolport_field.setText(str(self.settings_dict["port"]))

    def save_changes(self):
        """Saves changes to a JSON file."""
        self.settings_dict["radio_name"] = self.radioname_field.text()
        self.settings_dict["key"] = self.cloudlogapi_field.text()
        self.settings_dict["cloudurl"] = self.cloudlogurl_field.text()
        self.settings_dict["host"] = self.rigcontrolip_field.text()
        self.settings_dict["port"] = int(self.rigcontrolport_field.text())
        if self.rigctld_radioButton.isChecked():
            self.settings_dict["CAT_type"] = "rigctld"
        if self.flrig_radioButton.isChecked():
            self.settings_dict["CAT_type"] = "flrig"
        home = os.path.expanduser("~")
        with open(home + "/.cloudlogpycat.json", "wt", encoding="utf-8") as file_handle:
            file_handle.write(dumps(self.settings_dict))


app = QtWidgets.QApplication(sys.argv)
app.setStyle("Fusion")
font_dir = relpath("font")
families = load_fonts_from_dir(os.fspath(font_dir))
logging.info(families)
window = MainWindow()
window.show()
window.loadsaved()
# window.rigconnect()
timer = QtCore.QTimer()
timer.timeout.connect(window.mainloop)
timer.start(1000)
app.exec()
