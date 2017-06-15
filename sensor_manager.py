#######################################################################
# Writen by: Derek Santos
#######################################################################

from threading import Thread
from sensor_client import *

class Sensor_Manager():
    def __init__(self):
        # Creating the sensor_client list
        self.sensor_list = []
        # Creating a list for threads
        self.thread_list_frequency = []
        #self.thread_list_resistance = []

    def add_device(self, address):
        # Checks to see if device MAC_Address is already in the list
        same_mac_address_found = False
        for sensor in self.sensor_list:
            if sensor.address == address:
                same_mac_address_found = True
        if same_mac_address_found:
            return
        # Creation of the Sensor_Client object by passing in a MAC Address
        new_sensor = Sensor_Client(address)

        # Sensor_Client object then gets sent to the last position of the object
        self.sensor_list.append(new_sensor)

        # Knowing that lists stay in order, we can involke it's run function into a thread
        new_thread_frequency = Thread(target = self.sensor_list[len(self.sensor_list) - 1].run, args = ())

        # The thread will act as a daemon
        # When the main thread closes, all daemon threads will as well
        new_thread_frequency.daemon = True

        # The new frequency thread object gets sent the the back of the list and will start
        self.thread_list_frequency.append(new_thread_frequency)
        self.thread_list_frequency[len(self.thread_list_frequency) - 1].start()

        ## The new resistance thread object gets sent the the back of the list and will start
        #new_thread_resistance = Thread(target = self.sensor_list[len(self.sensor_list) - 1].request_resistance, args = ())
        #new_thread_resistance.daemon = True
        #self.thread_list_resistance.append(new_thread_resistance)
        #self.thread_list_resistance[len(self.thread_list_resistance) - 1].start()

    def list_devices(self):
        # For ever sensor_client in the sensor list, we will print it's information
        for position, device in enumerate(self.sensor_list):
            print ('{} - Sensor Address: {}, Connected: {}, Hv Value: {}, Hv Hex: {}, Reading fequency: {}, Reading Resistance: {}'.format(position + 1,
                                                                               device.address,
                                                                               device.connected,
                                                                               device.hv,
                                                                               hex(device.hv),
                                                                               device.reading_frequency,
                                                                               device.reading_resistance))
    # Given a position on the sensor_list, this function will change the hv value of the sensor
    def change_hv_value(self, pos, value):
        self.sensor_list[pos].change_hv_value(value)

    def remove_device(self, pos):
        # Involkes the disconnect function of sensor_client
        self.sensor_list[pos].disconnect()

        # Removes the thread and sensor objects from their respective lists
        self.thread_list_frequency.remove(self.thread_list_frequency[pos])
        #self.thread_list_resistance.remove(self.thread_list_resistance[pos])
        self.sensor_list.remove(self.sensor_list[pos])

    def remove_all_devices(self):
        for sensor in self.sensor_list:
            sensor.disconnect()
            self.sensor_list.remove(sensor)

        for thread in self.thread_list_frequency:
            self.thread_list_frequency.remove(thread)

        #for thread in self.thread_list_resistance:
        #    self.thread_list_resistance.remove(thread)

    def connect_device(self, pos):
        try:
            self.sensor_list[pos].connect()
        except Exception as e:
            print ('ERROR:', e)

    # Starting device reading
    def start_device_frequency(self, pos):
        # If device hasn't already started reading
        # reading_frequency will be set as true
        if not self.sensor_list[pos].reading_frequency:
            self.sensor_list[pos].reading_frequency = True

    def start_device_resistance(self, pos):
        # If device hasn't already started reading
        # reading_frequency will be set as true
        if not self.sensor_list[pos].reading_resistance:
            self.sensor_list[pos].reading_resistance = True

    #Stop device reading
    def stop_device_frequency(self, pos):
        if self.sensor_list[pos].reading_frequency:
            self.sensor_list[pos].reading_frequency = False

    def stop_device_resistance(self, pos):
        if self.sensor_list[pos].reading_resistance:
            self.sensor_list[pos].reading_resistance = False

    def start_all_devices(self):
         # Sets all devices in the sensor_list to start reading values
        for sensor in self.sensor_list:
            sensor.reading_frequency = True
            sensor.reading_resistance = True

    def stop_all_devices(self):
        # Sets all devices in the sensor_list to stop reading values
        for sensor in self.sensor_list:
            sensor.reading_frequency = False
            sensor.reading_resistance = False
