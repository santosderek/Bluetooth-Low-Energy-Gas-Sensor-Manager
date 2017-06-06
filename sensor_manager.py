from threading import Thread
from sensor_client import * 

class Sensor_Manager():
    def __init__(self):
        # Creating the sensor_client list
        self.sensor_list = []
        # Creating a list for threads 
        self.thread_list = []

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
        new_thread = Thread(target = self.sensor_list[len(self.sensor_list) - 1].run, args = ())

        # The thread will act as a daemon
        # When the main thread closes, all daemon threads will as well
        new_thread.daemon = True

        # The new thread object gets sent the the back of the list and will start
        self.thread_list.append(new_thread)
        self.thread_list[len(self.thread_list) - 1].start()

    
    def list_devices(self):
        # For ever sensor_client in the sensor list, we will print it's information
        for position, device in enumerate(self.sensor_list):
            print ('{} - Sensor Address: {}, Connected: {}, Hv Value: {}, Hv Hex: {}, Read: {}'.format(position + 1,
                                                                               device.address,
                                                                               device.connected,
                                                                               device.hv,
                                                                               hex(device.hv),
                                                                               device.reading_channels))
    # Given a position on the sensor_list, this function will change the hv value of the sensor
    def change_hv_value(self, pos, value):
        self.sensor_list[pos].change_hv_value(value)
        
        
    def remove_device(self, pos):
        # Involkes the disconnect function of sensor_client
        self.sensor_list[pos].disconnect()

        # Removes the thread and sensor objects from their respective lists
        self.thread_list.remove(self.thread_list[pos])
        self.sensor_list.remove(self.sensor_list[pos])

    def remove_all_devices(self):
        for sensor in self.sensor_list:
            sensor.disconnect()
            self.sensor_list.remove(sensor)

        for thread in self.thread_list:
            self.thread_list.remove(thread)

    def connect_device(self, pos):
        try: 
            self.sensor_list[pos].connect()
        except Exception as e:
            
            print ('ERROR:', e)
        
    def start_device(self, pos):
        # If device hasn't already started reading
        # reading_channels will be set as true
        if not self.sensor_list[pos].reading_channels: 
            self.sensor_list[pos].reading_channels = True

    def stop_device(self, pos):
        if self.sensor_list[pos].reading_channels:
            self.sensor_list[pos].reading_channels = False

    def start_all_devices(self):
         # Sets all devices in the sensor_list to start reading values
        for sensor in self.sensor_list:
            sensor.reading_channels = True

    def stop_all_devices(self):
        # Sets all devices in the sensor_list to stop reading values
        for sensor in self.sensor_list:
            sensor.reading_channels = False
