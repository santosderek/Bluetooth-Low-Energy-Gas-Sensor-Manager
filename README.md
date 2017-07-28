Bluetooth-LE-Gas-Sensor-Client
==============================
Retrieve data from a CMUT gas sensor using Bluetooth LE

Writen by: Derek Santos

Written by: Derek Santos
------------------------

Requirements
------------
* Python 3.x
* PyQt5
* PyGatt
* Known to run on Windows and Linux

How to install
--------------

#### Windows and OSX:
The following are the commands used with pip3 installed.

> pip3 install pygatt

> pip3 install pyqt5

Next if you have git install in your computer you can run:
> git clone https://github.com/santosderek/Bluetooth-Low-Energy-Gas-Sensor-Manager/

...or click the "Download" button on the github page.

Lastly, configure the config.py as intended, and run the following command within the sensor_client directory:
> python3 main.py

*** If on OSX you might need to use 'sudo' before the command. ***

#### Linux:
The following commands are within linux_install.sh.

You can run:
> bash linux_install.sh

Or can install using the following commands in order:
> sudo apt-get update

> sudo apt-get upgrade

> sudo apt-get install python3=3.5.1-3

> sudo apt-get install python3-pyqt5

> sudo apt-get install python3-pip

> sudo pip3 install pygatt

> sudo apt-get install -y git

Next if you have git install in your computer you can run:
> git clone https://github.com/santosderek/Bluetooth-Low-Energy-Gas-Sensor-Manager/

...or click the "Download" button on the github page.

Lastly, configure the config.py as intended, and run the following command within the sensor_client directory:
> python3 main.py

*** You might need to use 'sudo' before the command. ***

#### Optional


The setup.py is only after you have installed the dependencies.

This will allow you to run the command 'sensormanager' to run the script from any directory.
