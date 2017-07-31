import os
import pygatt

# Records the path to config.py
DIRECTORY_OF_FILE = os.path.dirname(os.path.realpath(__file__))
DIRECTORY_OF_SENSOR_DATA = DIRECTORY_OF_FILE + '/sensor_data/'
# Creates the ADAPTER variable
ADAPTER = None
ADDRESS_TYPE = pygatt.BLEAddressType.random

# Sensor Handles
READ_UUID = '2d30c082-f39f-4ce6-923f-3484ea480596'
WRITE_HANDLE = 0x0014
READ_HANDLE = 0x0011

# Frequency Channels
CHANNELS = [0x00, 0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70]
# List of bool variables that allows the plotting of it's respective channeel
# If a position is set to False, it will not record the data from that channel
ACTIVE_CHANNEL_LIST = [True for count in range(len(CHANNELS))]

# Resistance Constants
RL = 2.7
VREF = 3.3
VLSB = VREF / 1023.0
VOCM = 3.162
R1 = 100
A0 = -0.665
VICM = 1.9
VC = 5
