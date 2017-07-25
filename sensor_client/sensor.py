from PyQt5.QtCore import QThread
import pygatt

import sys
import binascii
import struct

import json
from time import time, ctime

from config import *

try:
    global ADAPTER
    ADAPTER = pygatt.BGAPIBackend()
    ADAPTER.start()
except pygatt.exceptions.NotConnectedError:
    not_connected = True
    while not_connected:
        try:
            ADAPTER = pygatt.BGAPIBackend()
            ADAPTER.start()
            not_connected = False
        except pygatt.exceptions.NotConnectedError as e:
            print(e)
        except Exception as e:
            print(e)


# Returns the voltage using the digital integer value
def get_voltage_out(digital_int_value, R2, ROFF):
    print(digital_int_value)
    return 1.24 * (1 + (R2 / (dtap_to_rhvpot(digital_int_value) + ROFF) ) )

def dtap_to_rhvpot(digital_int_value):
    # Result is returned in Kili-Ohm
    print(digital_int_value)
    return digital_int_value * (100 / 127)


def scan_for_nearby_ble_devices():
    list_of_devices = ADAPTER.scan(timeout = 3)
    return list_of_devices



class Sensor(QThread):
    def __init__(self, name, mac_address):
        QThread.__init__(self)

        self.name = name
        self.mac_address = mac_address

        self.sensor_running = True

        try:
            self.device = ADAPTER.connect(self.mac_address, address_type = ADDRESS_TYPE)
            self.device.subscribe(READ_UUID, callback = self.subcription_callback)
        except pygatt.exceptions.NotConnectedError:
            self.device = None
        except Exception as e:
            self.device = None

        self.subcription_response = None

        self.record_frequency = False
        self.record_resistance = False
        self.record_temperature = False
        self.record_humidity = False
        self.record_pressure = False

        self.gate_time = 100
        self.voltage = 0x60
        self.R2 = 1000
        self.ROFF = 50

    def __del__(self):
        self.sensor_running = False
        self.wait()

    def convert_voltage(self):
        return get_voltage_out(self.voltage, self.R2, self.ROFF)

    def change_voltage(self, value):
        print(value)
        self.voltage = int(value)
        self.device.char_write_handle(WRITE_HANDLE, bytearray([0x02, 0x00, value]))

    def run(self):
        start_time = time()
        filename = '{}-{}-{}.json'.format(self.name,self.mac_address.replace(':','_'), ctime(start_time).replace(':', '_'))

        data_list = []

        with open(DIRECTORY_OF_SENSOR_DATA + filename, mode='w', encoding='utf-8') as current_file:
            json.dump([], current_file)

        while self.sensor_running:
            try:
                if self.device is None:
                    self.connect_until_accepted()
                summary_dict = {'frequency':{'time':time()-start_time,  'value':{0:None,
                                                                                1:None,
                                                                                2:None,
                                                                                3:None,
                                                                                4:None,
                                                                                5:None,
                                                                                6:None,
                                                                                7:None,
                                                                                }
                                            },
                                'resistance': {'time':time()-start_time, 'value':None},

                                'temperature':{'time':time()-start_time, 'value':None},

                                'pressure':   {'time':time()-start_time, 'value':None},

                                'humidity':   {'time':time()-start_time, 'value':None},

                                }

                if self.record_frequency:

                    for channel_position in range(len(CHANNELS)):
                        summary_dict['frequency']['value'][channel_position] = self.read_frequency(CHANNELS[channel_position])

                if self.record_resistance:
                    summary_dict['resistance']['value'] = self.read_resistance()

                if self.record_temperature:
                    summary_dict['temperature']['value'] = self.read_temperature()

                if self.record_pressure:
                    summary_dict['pressure']['value'] = self.read_pressure()

                if self.record_humidity:
                    summary_dict['humidity']['value'] = self.read_humidity()


                if summary_dict['frequency']['value'] is None and \
                    summary_dict['resistance']['value'] is None and \
                    summary_dict['temperature']['value'] is None and \
                    summary_dict['pressure']['value'] is None and \
                    summary_dict['humidity']['value'] is None:
                    continue

                with open(DIRECTORY_OF_SENSOR_DATA + filename, mode='w', encoding='utf-8') as current_file:

                    data_list.append(summary_dict)
                    json.dump(data_list, current_file)
            except pygatt.exceptions.NotConnectedError as e:
                self.connect_until_accepted()

            except Exception as e:
                print ('ERROR: Sensor:', e)




    def connect_until_accepted(self):
        not_connected = True

        while not_connected:
            try:
                self.device = ADAPTER.connect(self.mac_address, address_type = ADDRESS_TYPE)
                self.device.subscribe(READ_UUID, callback = self.subcription_callback)
                not_connected = False
            except pygatt.exceptions.NotConnectedError:
                self.device = None
                #sleep(1)
            except Exception as e:
                self.device = None
                #sleep(1)

    def subcription_callback(self, handle, data):
        self.subcription_response = data

    def read_frequency(self, channel):
        try:
            self.device.char_write_handle(WRITE_HANDLE, bytearray([0x04, 0x80, channel + 0x8a]))
            self.device.char_write_handle(WRITE_HANDLE, bytearray([0x04, 0x80, channel + 0x8b]))

            # gate time = 100 ms
            self.device.char_write_handle(WRITE_HANDLE, bytearray([0x05, 0x01, self.gate_time]))

            # read frequency
            self.device.char_write_handle(WRITE_HANDLE, bytearray([0x04, 0x08, 0x04]))

            while self.subcription_response is None:
                pass

            #print(self.subcription_response)
            count = struct.unpack('<I', binascii.unhexlify(self.subcription_response.hex()))[0]

            # Formula to convert the count recieved from Hz to MHz
            frequency = float(count) / float(2) / (self.gate_time / 1000.0) / 1000000.0

            return frequency

        except Exception as e:
            print ('Channel %d' % channel, e)

        finally:
            self.subcription_response = None

    def read_resistance(self):
        try:
            # read resistance
            self.device.char_write_handle(WRITE_HANDLE, bytearray([0x04]))

            while self.subcription_response is None:
                pass


            digital_value = struct.unpack('<I', binascii.unhexlify(self.subcription_response.hex()))[0]

            # Formula to convert the count recieved from Hz to MHz
            voltage_ref = 3.3
            vlsb = voltage_ref / 1023.0
            vlog = digital_value * vlsb
            vc = 5
            rl = 2.2
            # Calculate resistance
            resistance = (vc - vlog) * rl / vlog


            return resistance

        except Exception as e:
            print (e)

        finally:
            self.subcription_response = None

    def read_temperature(self):
        try:
            # read Temperature
            self.device.char_write_handle(WRITE_HANDLE, bytearray([0x06]))

            while self.subcription_response is None:
                pass

            temperature_float = struct.unpack('<f', binascii.unhexlify(self.subcription_response.hex()))[0]

            return temperature_float

        except Exception as e:
            print ('ERROR: Temperature:', e)

        finally:
            self.subcription_response = None

    def read_pressure(self):
        try:
            # read Pressure
            self.device.char_write_handle(WRITE_HANDLE, bytearray([0x07]))

            while self.subcription_response is None:
                pass

            pressure_float = struct.unpack('<f', binascii.unhexlify(self.subcription_response.hex()))[0]

            return pressure_float

        except Exception as e:
            print ('ERROR: Temperature:', e)

        finally:
            self.subcription_response = None

    def read_humidity(self):
        try:
            # read Pressure
            self.device.char_write_handle(WRITE_HANDLE, bytearray([0x08]))

            while self.subcription_response is None:
                pass

            humidity_float = struct.unpack('<f', binascii.unhexlify(self.subcription_response.hex()))[0]

            return humidity_float

        except Exception as e:
            print ('ERROR: Temperature:', e)

        finally:
            self.subcription_response = None
