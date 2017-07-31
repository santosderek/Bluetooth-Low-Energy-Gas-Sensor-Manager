# 3rd party modules
from PyQt5.QtCore import QThread
import pygatt

# Python Modules
import sys
import struct
import json
from time import time, ctime, sleep
import os

from config import *

# Allows error to print once
adapter_print_bool = False

""" Loop until the adapter was found and connected to """
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
            if not adapter_print_bool:
                print(e)
                adapter_print_bool = True
            sleep(1)
        except Exception as e:
            if not adapter_print_bool:
                print(e)
                adapter_print_bool = True
            sleep(1)

""" If the sensor data folder is not found, make one """
if not os.path.exists(DIRECTORY_OF_SENSOR_DATA):
    os.mkdir(DIRECTORY_OF_SENSOR_DATA)


def get_voltage_out(digital_int_value, R2, ROFF):
    """ Returns the voltage using the digital integer value """
    return 1.24 * (1 + (R2 / (dtap_to_rhvpot(digital_int_value) + ROFF)))


def dtap_to_rhvpot(digital_int_value):
    """ Result is returned in Kili-Ohm """
    return digital_int_value * (100 / 127)


def scan_for_nearby_ble_devices():
    """ Returns a list of nearby devices """
    try:
        list_of_devices = ADAPTER.scan(timeout=3)
        return list_of_devices
    except Exception as e:
        print(e)
        return []


class Sensor(QThread):
    def __init__(self, name, mac_address):
        QThread.__init__(self)

        self.name = name
        self.mac_address = mac_address

        self.sensor_running = True

        try:
            self.device = ADAPTER.connect(
                self.mac_address, address_type=ADDRESS_TYPE)
            self.device.subscribe(
                READ_UUID, callback=self.subcription_callback)
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
        self.set_voltage = 0x60
        self.R2 = 1000
        self.ROFF = 50

    def __del__(self):
        self.sensor_running = False
        self.wait()

    def convert_voltage(self):
        """ Converts the current hex number to voltage """
        return get_voltage_out(self.voltage, self.R2, self.ROFF)

    def change_voltage(self, value):
        """ Changes the current voltage value """
        self.set_voltage = int(value)

    def run(self):
        """ Loop and record the data from the current sensor """
        start_time = time()
        filename = '{}-{}-{}.json'.format(self.name, self.mac_address.replace(
            ':', '_'), ctime(start_time).replace(':', '_'))

        data_list = []

        with open(DIRECTORY_OF_SENSOR_DATA + filename, mode='w', encoding='utf-8') as current_file:
            json.dump([], current_file)

        while self.sensor_running:
            try:

                if self.device is None:
                    self.connect_until_accepted()

                summary_dict = {'frequency': {'time': time() - start_time,
                                              'value': {0: None,
                                                        1: None,
                                                        2: None,
                                                        3: None,
                                                        4: None,
                                                        5: None,
                                                        6: None,
                                                        7: None}},

                                'resistance': {'time': time() - start_time, 'value': None},

                                'temperature': {'time': time() - start_time, 'value': None},

                                'pressure':   {'time': time() - start_time, 'value': None},

                                'humidity':   {'time': time() - start_time, 'value': None},

                                }

                if self.set_voltage != self.voltage:
                    try:
                        print(self.set_voltage)
                        self.device.char_write_handle(WRITE_HANDLE, bytearray(
                            [0x02, 0x00, int(self.set_voltage)]), wait_for_response=False)
                        sleep(5)
                        self.voltage = self.set_voltage
                        print(self.voltage)
                    except Exception as e:
                        print(e)

                if self.record_frequency:

                    for channel_position in range(len(CHANNELS)):
                        if ACTIVE_CHANNEL_LIST[channel_position]:
                            summary_dict['frequency']['value'][channel_position] = self.read_frequency(
                                CHANNELS[channel_position])

                if self.record_resistance:
                    summary_dict['resistance']['value'] = self.read_resistance()

                if self.record_temperature:
                    summary_dict['temperature']['value'] = self.read_temperature()

                if self.record_pressure:
                    summary_dict['pressure']['value'] = self.read_pressure()

                if self.record_humidity:
                    summary_dict['humidity']['value'] = self.read_humidity()

            except pygatt.exceptions.NotConnectedError as e:
                self.connect_until_accepted()

            except Exception as e:
                print('ERROR: Sensor:', e)

            finally:
                if summary_dict['frequency']['value'] is None and \
                        summary_dict['resistance']['value'] is None and \
                        summary_dict['temperature']['value'] is None and \
                        summary_dict['pressure']['value'] is None and \
                        summary_dict['humidity']['value'] is None:
                    pass
                else:

                    with open(DIRECTORY_OF_SENSOR_DATA + filename, mode='w', encoding='utf-8') as current_file:
                        data_list.append(summary_dict)
                        json.dump(data_list, current_file)
                    sleep(.5)

    def connect_until_accepted(self):
        """ Loop until the current device has connected """
        not_connected = True

        while not_connected:
            try:
                self.device = ADAPTER.connect(
                    self.mac_address, address_type=ADDRESS_TYPE)
                self.device.subscribe(
                    READ_UUID, callback=self.subcription_callback)
                not_connected = False
            except pygatt.exceptions.NotConnectedError:
                self.device = None
            except Exception as e:
                self.device = None

    def subcription_callback(self, handle, data):
        """ Record the data recieved from the sensor """
        self.subcription_response = data

    def read_frequency(self, channel):
        """ Record the frequency from the sensor """
        try:
            self.device.char_write_handle(WRITE_HANDLE, bytearray(
                [0x04, 0x80, channel + 0x80 + 0x0a]))
            self.device.char_write_handle(WRITE_HANDLE, bytearray(
                [0x04, 0x80, channel + 0x80 + 0x0b]))

            # gate time = 100 ms
            self.device.char_write_handle(
                WRITE_HANDLE, bytearray([0x05, 0x00, self.gate_time]))

            # read frequency
            self.device.char_write_handle(
                WRITE_HANDLE, bytearray([0x04, 0x08, 0x04]))

            while self.subcription_response is None:
                pass

            count = struct.unpack('<I', bytes(self.subcription_response))[0]

            # Formula to convert the count recieved from Hz to MHz
            frequency = float(count) / float(2) / \
                (self.gate_time / 1000.0) / 1000000.0

            return frequency

        except Exception as e:
            print('Channel %d' % channel, e)

        finally:
            self.subcription_response = None

    def v2r_scaled(self, v):
        vin = (v - VOCM) / A0
        i = (vin - VICM) / R1
        r_sensor = (VC * RL - vin * RL) / (vin + RL * i)
        return r_sensor

    def read_resistance(self):
        """ Record the resistance from the sensor """

        try:
            # read resistance
            self.device.char_write_handle(WRITE_HANDLE, bytearray([0x04]))

            while self.subcription_response is None:
                pass

            digital_value = struct.unpack(
                '<I', bytes(self.subcription_response))[0]

            vlog = digital_value * VLSB
            # Calculate resistance
            resistance = self.v2r_scaled(vlog)

            return resistance

        except Exception as e:
            print(e)

        finally:
            self.subcription_response = None

    def read_temperature(self):
        """ Record the Temperature from the sensor """
        try:
            # read Temperature
            self.device.char_write_handle(WRITE_HANDLE, bytearray([0x06]))

            while self.subcription_response is None:
                pass

            temperature_float = struct.unpack(
                '<f', bytes(self.subcription_response))[0]

            return temperature_float

        except Exception as e:
            print('ERROR: Temperature:', e)

        finally:
            self.subcription_response = None

    def read_pressure(self):
        """ Record the pressure from the sensor """
        try:
            # read Pressure
            self.device.char_write_handle(WRITE_HANDLE, bytearray([0x07]))

            while self.subcription_response is None:
                pass

            pressure_float = struct.unpack(
                '<f', bytes(self.subcription_response))[0]

            return pressure_float

        except Exception as e:
            print('ERROR: Temperature:', e)

        finally:
            self.subcription_response = None

    def read_humidity(self):
        """ Record the humidity from the sensor """
        try:
            # read Pressure
            self.device.char_write_handle(WRITE_HANDLE, bytearray([0x08]))

            while self.subcription_response is None:
                pass

            humidity_float = struct.unpack(
                '<f', bytes(self.subcription_response))[0]

            return humidity_float

        except Exception as e:
            print('ERROR: Temperature:', e)

        finally:
            self.subcription_response = None
