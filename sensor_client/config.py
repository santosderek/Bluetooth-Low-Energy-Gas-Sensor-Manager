import os
DIRECTORY_OF_FILE = os.path.dirname(os.path.realpath(__file__))
DIRECTORY_OF_SENSOR_DATA = DIRECTORY_OF_FILE + '/sensor_data/'

import pygatt
ADAPTER = None
ADDRESS_TYPE = pygatt.BLEAddressType.random

READ_UUID = '2d30c082-f39f-4ce6-923f-3484ea480596'
CHANNELS = [0x00, 0x10,0x20,0x30,0x40,0x50,0x60,0x70]
WRITE_HANDLE = 0x0014
READ_HANDLE = 0x0011
