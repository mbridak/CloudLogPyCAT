# CloudLogPyCAT

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)  [![Python: 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)  [![Made With:PyQt5](https://img.shields.io/badge/Made%20with-PyQt5-red)](https://pypi.org/project/PyQt5/)  

![cloud cat](https://github.com/mbridak/CloudLogPyCAT/raw/master/pic/cloudcat.png)

Python client to query the CAT interface and report radio frequency/mode to CloudLog

Written in Python3, using QT5. Either run from source, or if your running Linux, download the binary [here](https://github.com/mbridak/CloudLogPyCAT/releases/download/21.5.14/CloudLogPyCAT)

![main screen](./pic/screen.png)

## Running on Apple Silicon

@m1geo Notes that He is able to run this on Apple M1 by using Qt6.

## Changes since release 21.5.14 Clumpy Litter

I Made made a CAT class. So now the it handles both rigctld and flrig.

For Debian based Linux or Raspberry OS you can:

`sudo apt install flrig`

or

`sudo apt install hamlibtools`

## Running from source

Install Python 3, then two required libraries.

If you're the Ubuntu/Debian type you can:

`sudo apt install python3-pyqt5 python3-requests`

You can install libraries via pip:

`python3 -m pip3 install -r requirements.txt`

Just make tuner.py executable and run it within the same folder, or type:

`python3 CloudLogPyCAT.py`

## Building a binary executable

I've included a .spec file in case you wished to create your own binary from the source. To use it, first install pyinstaller.

`python3 -m pip3 install pyinstaller`

Then build the binary.

`pyinstaller -F CloudLogPyCAT.spec`

Look in the newly created dist directory to find your binary.

## First run

When run for the first time click the settings button and edit the needed bits.

![settings screen](pic/settings.png)

Then be sure to select your radio under the station tab while on the QSO screen for the updated band/mode data to show.

I've updated the desktop icon to be 3d animated. When you try and click on it to launch the program, the cat will bat the mouse away with it's paws.

That last part was BS. Just checking to see if you were paying attention.
