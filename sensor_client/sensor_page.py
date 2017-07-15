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

from time import ctime

from sensor_client import *
from config import *
from hcitool import *


class Sensor_Manager_Frame(Frame):
    def __init__(self, parent_container):
        Frame.__init__(self, parent_container)
        self.parent_container = parent_container

        self.scan_frame = Sensor_Scan_Frame(self)
        self.scan_frame.pack(side = TOP, fill = BOTH, expand = False)

        self.sensor_collection_frame = Sensor_Collection_Frame(self)
        self.sensor_collection_frame.pack(side = TOP, fill = BOTH, expand = True)

class Sensor_Collection_Frame(Frame):
    def __init__(self, parent_container):
        Frame.__init__(self, parent_container)
        self.parent_container = parent_container

        Label (self, text = 'Sensors', font = LARGE_FONT).pack(side = TOP, fill = BOTH, expand = False)
        self.list_of_sensor_node_frames = []

        #TODO: This is only for testing... Delete
        self.list_of_sensor_node_frames.append(Sensor_Node_Frame(self, '', 'FD:4E:4D:5B:4D:1B'))
        for s_node in self.list_of_sensor_node_frames:
            s_node.pack(side = TOP, fill = BOTH, expand = False)

    def add_sensor_node(self, passedName):
        name, mac_address = passedName.split ('-')
        name.replace(' ', '')
        mac_address = re.search('\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2}', mac_address).group(0)

        for sensor in self.list_of_sensor_node_frames:
            if sensor.mac_address == mac_address:
                return

        self.list_of_sensor_node_frames.append(Sensor_Node_Frame(self, name, mac_address))
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

        # Bool to see if device is scanning
        self.is_scanning = False

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

        self.scan_thread = None

    def add_sensor(self):
        cursor_selection = self.list_box.curselection()
        if cursor_selection == ():
            return
        listbox_selection = self.list_box.get(cursor_selection)
        self.parent_container.sensor_collection_frame.add_sensor_node(listbox_selection)

    def new_thread_scan(self):
        if not self.is_scanning:
            try:
                self.scan_thread = Thread(target=self.scan_for_devices, args = ())
                self.scan_thread.start()

            except Exception as e:
                self.list_box.delete(0, END)
                self.list_box.insert (END, 'Can not create thread...')


    def scan_for_devices (self):
        try:
            self.is_scanning = True
            self.list_box.delete(0, END)
            self.list_box.insert (END, 'Scanning...')
            #scan_results = ble_scan()
            hcitool = HCITOOL()
            scan_results = hcitool.read_output()

            print(scan_results)
            self.list_box.delete(0, END)

            if scan_results is None:
                self.list_box.insert (END, 'Nothing Found. Make Sure Root.')
                return

            # The first line is always 'Scanning...'
            for line in scan_results[1:]:
                
                line = line.split(' ')
                self.list_box.insert(END, '{} - {}'.format (line[1], line[0]))

        except Exception as e:
            self.list_box.delete(0, END)
            self.list_box.insert (END, 'Can not complete scan...')
            print('ERROR: Scanning:', e)

        finally:
            self.is_scanning = False

class Sensor_Node_Frame(Frame):
    def __init__(self, parent_container, name, mac_address):
        Frame.__init__(self, parent_container)

        self.parent_container = parent_container

        self.name = str(name)
        self.mac_address = str(mac_address)
        self.sensor = Sensor_Client(mac_address)

        self.name_string_var = StringVar()
        self.name_string_var.set(str(name + ' ' + mac_address))
        self.connected_string_var = StringVar()
        self.connected_string_var.set('Connected')
        self.reading_frequency_string_var = StringVar()
        self.reading_frequency_string_var.set('Reading Frequency')
        self.reading_resistance_string_var = StringVar()
        self.reading_resistance_string_var.set('Reading Resistance')
        self.voltage_var = StringVar()
        self.voltage_var.set('Voltage: ' + str(self.sensor.high_voltage))
        self.reading_environment_string_var = StringVar()
        self.reading_environment_string_var.set('Reading Environment')

        self.sensor_connect_button_stringvar = StringVar()
        self.sensor_connect_button_stringvar.set('Connect')

        self.sensor_name_label = Label(self, textvariable = self.name_string_var)
        self.sensor_connected_label = Label(self, textvariable = self.connected_string_var)
        self.sensor_reading_frequency_label = Label(self, textvariable = self.reading_frequency_string_var)
        self.sensor_reading_resistance_label = Label(self, textvariable = self.reading_resistance_string_var)
        self.sensor_reading_environment_label = Label(self, textvariable = self.reading_environment_string_var)
        self.sensor_voltage_label = Label(self, textvariable = self.voltage_var)

        self.sensor_connect_button = ttk.Button(self, textvariable = self.sensor_connect_button_stringvar, command = self.connect_to_sensor)
        self.sensor_disconnect_button = ttk.Button(self, text = 'Disconnect', command = self.sensor.disconnect)
        self.sensor_read_frequency_button = ttk.Button(self, text = 'Read Frequency', command = self.toggle_reading_frequency)
        self.sensor_read_resistance_button = ttk.Button(self, text = 'Read Resistance', command = self.toggle_reading_resistance)
        self.sensor_environment_button = ttk.Button(self, text = 'Read Environment', command = self.toogle_read_environment)
        self.sensor_settings_button = ttk.Button(self, text = 'Settings', command = self.show_settings)

        self.sensor_connected_label.config (fg = 'red')
        self.sensor_reading_frequency_label.config (fg = 'red')
        self.sensor_reading_resistance_label.config (fg = 'red')

        self.sensor_name_label.pack(side = LEFT, fill = BOTH, expand = True)
        self.sensor_connected_label.pack(side = LEFT, fill = BOTH, expand = True)
        self.sensor_reading_frequency_label.pack(side = LEFT, fill = BOTH, expand = True)
        self.sensor_reading_resistance_label.pack(side = LEFT, fill = BOTH, expand = True)
        self.sensor_reading_environment_label.pack(side = LEFT, fill = BOTH, expand = True)
        self.sensor_voltage_label.pack(side = LEFT, fill = BOTH, expand = True)

        self.sensor_connect_button.pack(side = LEFT, fill = BOTH, expand = True)
        self.sensor_disconnect_button.pack(side = LEFT, fill = BOTH, expand = True)
        self.sensor_read_frequency_button.pack(side = LEFT, fill = BOTH, expand = True)
        self.sensor_read_resistance_button.pack(side = LEFT, fill = BOTH, expand = True)
        self.sensor_environment_button.pack(side = LEFT, fill = BOTH, expand = True)
        self.sensor_settings_button.pack(side = LEFT, fill = BOTH, expand = True)

        # Creation of update_labels thread
        self.update_labels_thread = Thread(target = self.update_labels,
                                           args = (),
                                           daemon=True)
        self.update_labels_thread.start()

    def show_settings(self):
        settings_child_window = Sensor_Settings(self, self.sensor)
        settings_child_window.grab_set()

    def connect_to_sensor(self):
        self.sensor_connect_button_stringvar.set('Connecting')
        sleep(1)
        self.sensor.connect()
        self.sensor_connect_button_stringvar.set('Connect')



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

    def toogle_read_environment(self):
        if self.sensor.reading_environment:
            self.sensor.reading_environment = False
        else:
            self.sensor.reading_environment = True

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

            if self.sensor.reading_environment:
                self.sensor_reading_environment_label.config(fg = 'green')
            else:
                self.sensor_reading_environment_label.config(fg = 'red')
            converted_voltage = get_voltage_out(self.sensor.high_voltage, self.sensor.R2, self.sensor.ROFF)
            self.voltage_var.set('Voltage[ int:' + str(self.sensor.high_voltage) +
                                 ' | %.3f V' % converted_voltage + ' ]')

class Sensor_Settings(Toplevel):
    def __init__(self, parent_container, sensor):
        Toplevel.__init__(self, parent_container)

        self.parent_container = parent_container
        self.sensor = sensor

        self.voltage_frame = Sensor_Voltage_Frame(self, self.sensor)
        self.voltage_frame.pack(side = TOP, fill = BOTH, expand = False)

        self.gate_time_frame = Sensor_Gate_Time_Frame(self, self.sensor)
        self.gate_time_frame.pack(side = TOP, fill = BOTH, expand = False)

        self.reconnect_frame = Sensor_Reconnect_Frame(self, self.sensor)
        self.reconnect_frame.pack(side = TOP, fill = BOTH, expand = False)


class Sensor_Voltage_Frame(Frame):

    # NOTE: self.sensor.high_voltage is just an integer value that is converted from a hex value
    # Python automatically converts 0xXX to integer values
    def __init__(self, parent_container, sensor):
        Frame.__init__(self, parent_container)

        self.parent_container = parent_container
        self.sensor = sensor

        self.voltage_entry = Entry(self)
        self.up_button = Button(self, text = '+5', command = self.add_five)
        self.down_button = Button(self, text = '-5', command = self.subtract_five)
        self.change_using_entry_button = Button(self, text = 'Apply Voltage', command = self.change_using_entry)

        Label (self, text = 'Change Voltage:').pack(side = LEFT, fill = BOTH, expand = False)
        self.voltage_entry.pack(side = LEFT, fill = BOTH, expand = False)
        self.up_button.pack(side = LEFT, fill = BOTH, expand = False)
        self.down_button.pack(side = LEFT, fill = BOTH, expand = False)
        self.change_using_entry_button.pack(side = LEFT, fill = BOTH, expand = False)

    def change_using_entry(self):
        try:
            value = self.voltage_entry.get()
            if value == '':
                return
            if value[:2] == '0x':
                value_int = int(value, 16)
            else:
                self.change_using_entry_button.text = 'Changing...'
                sleep(1/2)
                value_int = int(value)
            self.sensor.change_hv_value(value_int)
            self.change_using_entry_button.text = 'Apply Voltage'
        except Exception as e:
            pass

    def add_five(self):
        self.sensor.change_hv_value(self.sensor.high_voltage + 5)

    def subtract_five(self):
        self.sensor.change_hv_value(self.sensor.high_voltage - 5)

class Sensor_Gate_Time_Frame(Frame):
    def __init__ (self, parent_container, sensor):
        Frame.__init__(self, parent_container)

        self.parent_container = parent_container
        self.sensor = sensor

        self.gate_time_text = StringVar()
        self.gate_time_text.set('Gate Time: %s (milliseconds)' % str(self.sensor.gate_time) )

        self.gate_time_entry = Entry(self)
        self.gate_time_entry.insert(0, str(self.sensor.gate_time))
        self.change_gate_time_button = Button (self, text = 'Change Gate Time', command = self.set_gate_time)

        Label(self, textvariable = self.gate_time_text).pack(side = LEFT, fill = BOTH, expand = False)
        self.gate_time_entry.pack(side = LEFT, fill = BOTH, expand = False)
        self.change_gate_time_button.pack(side = LEFT, fill = BOTH, expand = False)

    def set_gate_time (self):
        try:
            new_gate_time_string = self.gate_time_entry.get()
            if not new_gate_time_string == '':
                new_gate_time_int = int(new_gate_time_string)
                self.sensor.gate_time = new_gate_time_int
                self.gate_time_text.set('Gate Time: %s (milliseconds)' % str(self.sensor.gate_time) )


        except Exception as e:
            pass

class Sensor_Reconnect_Frame(Frame):
    def __init__(self, parent_container, sensor):
        Frame.__init__(self, parent_container)

        self.parent_container = parent_container
        self.sensor = sensor

        self.reconnecting_stringvar = StringVar()
        self.reconnecting_stringvar.set('Reconnecting')

        self.reconnecting_label = Label(self, text = 'Reconnecting')
        self.reconnecting_label.pack(side = LEFT, fill = BOTH, expand = False)

        if self.sensor.reconnecting_allowed:
            self.reconnecting_label.config(fg = 'green')
        else:
            self.reconnecting_label.config(fg = 'red')


        self.reconnect_button = Button(self, text = 'Toggle Reconnect', command = self.toggle_reconnect)
        self.reconnect_button.pack(side = LEFT, fill = BOTH, expand = False)

    def toggle_reconnect(self):
        if self.sensor.reconnecting_allowed:
            self.sensor.reconnecting_allowed = False
            self.reconnecting_label.config(fg = 'red')

        else:
            self.sensor.reconnecting_allowed = True
            self.reconnecting_label.config(fg = 'green')
