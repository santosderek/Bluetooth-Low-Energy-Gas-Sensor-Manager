import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation


from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from threading import Thread

import os

from sensor_client import *

from config import LARGE_FONT, NORMAL_FONT


class Sensor_Manager_Frame(Frame):
    def __init__(self, parent_container):
        Frame.__init__(self, parent_container)

        self.scan_frame = Sensor_Scan_Frame(self)
        self.scan_frame.pack(side = TOP, fill = BOTH, expand = False)

        self.sensor_node_frame = Frame(self)
        self.sensor_node_frame.pack(side = TOP, fill = BOTH, expand = True)
        self.sensor_node_label = Label (self.sensor_node_frame, text = 'Sensors', font = LARGE_FONT)
        self.sensor_node_label.pack(side = TOP, fill = BOTH, expand = False)

        self.list_of_sensor_node_frames = []

    def add_sensor_node(self, passedName):
        name, mac_address = passedName.split ('-')
        name.replace(' ', '')
        mac_address = re.search('\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2}', mac_address).group(0)

        for sensor in self.list_of_sensor_node_frames:
            if sensor.mac_address == mac_address:
                return

        self.list_of_sensor_node_frames.append(Sensor_Node_Frame(self.sensor_node_frame, name, mac_address))
        for s_node in self.list_of_sensor_node_frames:
            s_node.pack(side = TOP, fill = BOTH, expand = False)

    def disconnect_all_sensors(self):
        for sensor_frame in self.list_of_sensor_node_frames:
            sensor_frame.sensor.disconnect()

    def remove_sensor_node(self):
        pass


class Sensor_Scan_Frame(Frame):
    def __init__(self, parent_container):
        Frame.__init__(self, parent_container)
        self.parent_container = parent_container
        self.title_label = Label (self, text = 'Scan', font = LARGE_FONT)
        self.scan_button_frame = Frame(self)
        self.scan_list_frame = Frame(self)

        self.list_box = Listbox(self.scan_list_frame)
        self.scan_button = Button (self.scan_button_frame, text = 'Scan', command = self.scan_for_devices)
        self.add_sensor_node = Button (self.scan_button_frame, text = 'Add Sensor', command = self.add_sensor)

        self.title_label.pack(side = TOP, fill = BOTH, expand = False)
        self.scan_list_frame.pack(side = LEFT, fill = BOTH, expand = True)
        self.scan_button_frame.pack(side = RIGHT, fill = BOTH, expand = True)

        self.list_box.pack(side = LEFT, fill = BOTH, expand = True)
        self.scan_button.pack(side = RIGHT, fill = BOTH, expand = True)
        self.add_sensor_node.pack(side = RIGHT, fill = BOTH, expand = True)

    def add_sensor(self):
        cursor_selection = self.list_box.curselection()
        if cursor_selection == ():
            return
        listbox_selection = self.list_box.get(cursor_selection)
        self.parent_container.add_sensor_node(listbox_selection)

    def scan_for_devices (self):
        scan_results = ble_scan()
        self.list_box.delete(0, END)

        if scan_results is None:
            self.list_box.insert (END, 'Nothing Found')
            return

        for address, name in scan_results.items():
            self.list_box.insert(END, '{} - {}'.format (name, address))


class Sensor_Node_Frame(Frame):
    def __init__(self, parent_container, name, mac_address):
        Frame.__init__(self, parent_container)

        self.name = str(name)
        self.mac_address = str(mac_address)

        self.sensor = Sensor_Client(mac_address)

        self.name_string_var = StringVar()
        self.name_string_var.set(str(name + mac_address))
        self.connected_string_var = StringVar()
        self.connected_string_var.set('Connected')
        self.reading_frequency_string_var = StringVar()
        self.reading_frequency_string_var.set('Reading Frequency')
        self.reading_resistance_string_var = StringVar()
        self.reading_resistance_string_var.set('Reading Resistance')

        self.sensor_name_label = Label(self, textvariable = self.name_string_var)
        self.sensor_connected_label = Label(self, textvariable = self.connected_string_var)
        self.sensor_reading_frequency_label = Label(self, textvariable = self.reading_frequency_string_var)
        self.sensor_reading_resistance_label = Label(self, textvariable = self.reading_resistance_string_var)

        self.sensor_connect_button = ttk.Button(self, text = 'Connect', command = self.connect_to_sensor)
        self.sensor_disconnect_button = ttk.Button(self, text = 'Disconnect', command = self.sensor.disconnect)
        self.sensor_read_frequency_button = ttk.Button(self, text = 'Read Frequency', command = self.toggle_reading_frequency)
        self.sensor_read_resistance_button = ttk.Button(self, text = 'Read Resistance', command = self.toggle_reading_resistance)


        self.sensor_connected_label.config (fg = 'red')
        self.sensor_reading_frequency_label.config (fg = 'red')
        self.sensor_reading_resistance_label.config (fg = 'red')

        self.sensor_name_label.pack(side = LEFT, fill = BOTH, expand = True)
        self.sensor_connected_label.pack(side = LEFT, fill = BOTH, expand = True)
        self.sensor_reading_frequency_label.pack(side = LEFT, fill = BOTH, expand = True)
        self.sensor_reading_resistance_label.pack(side = LEFT, fill = BOTH, expand = True)

        self.sensor_connect_button.pack(side = LEFT, fill = BOTH, expand = True)
        self.sensor_disconnect_button.pack(side = LEFT, fill = BOTH, expand = True)
        self.sensor_read_frequency_button.pack(side = LEFT, fill = BOTH, expand = True)
        self.sensor_read_resistance_button.pack(side = LEFT, fill = BOTH, expand = True)

        # Creation of update_labels thread
        self.update_labels_thread = Thread(target = self.update_labels, args = ())
        self.update_labels_thread.daemon = True
        self.update_labels_thread.start()

    def connect_to_sensor(self):
        self.sensor.connect(connect_once = True)

    def toggle_reading_frequency(self):
        if self.sensor.reading_frequency:
            self.sensor.reading_frequency = False
        else:
            self.sensor.reading_frequency = True

    def toggle_reading_resistance(self):
        if self.sensor.reading_resistance:
            self.sensor.reading_resistance = False
        else:
            self.sensor.reading_resistance = True

    def update_labels(self):
        while True:
            if self.sensor.connected:
                self.sensor_connected_label.config(fg = 'green')
            else:
                self.sensor_connected_label.config(fg = 'red')

            if self.sensor.reading_frequency:
                self.sensor_reading_frequency_label.config(fg = 'green')
            else:
                self.sensor_reading_frequency_label.config(fg = 'red')

            if self.sensor.reading_resistance:
                self.sensor_reading_resistance_label.config(fg = 'green')
            else:
                self.sensor_reading_resistance_label.config(fg = 'red')
