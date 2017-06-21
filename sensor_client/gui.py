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

DIRECTORY_OF_FILE = os.path.dirname(os.path.realpath(__file__))
DIRECTORY_OF_SENSOR_DATA = DIRECTORY_OF_FILE + '/sensor_data/'

LARGE_FONT = ("Verdana", 12)
NORMAL_FONT = ("Verdana", 12)

def select_latest_file(directory = DIRECTORY_OF_SENSOR_DATA):
    latest_time = None
    latest_path = None
    first_loop = True
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            current_time = os.stat(file_path)
            if not first_loop and int(current_time.st_mtime) > int(latest_time.st_mtime):
                latest_time = os.stat(file_path)
                latest_path = file_path
            elif first_loop:
                latest_time = os.stat(file_path)
                latest_path = file_path
                first_loop = False
    return latest_path

class Main_Window(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        Tk.wm_title(self, 'Live Sensor GUI')

        main_frame = Frame(self)
        main_frame.pack( side = TOP, fill = BOTH, expand = True )
        main_frame.grid_rowconfigure(0, weight = 1 )
        main_frame.grid_columnconfigure(0, weight = 1 )

        # Creating the container that will hold the graph
        self.graph_page = Graph_Frame (main_frame)
        self.graph_page.grid (row = 0, column = 0, sticky = 'nsew')

        #Creating the Sensor_Manager_Frame page
        self.sensor_manager_page = Sensor_Manager_Frame(main_frame)
        self.sensor_manager_page.grid (row = 0, column = 0, sticky = 'nsew')


        # Initializing Variables
        self.file_name = None

        # Creating the menu bar
        menubar = Menu(main_frame)

        open_file_menu = Menu(menubar, tearoff = 0)
        open_file_menu.add_command( label = 'Open Sensor File',
                                    command = self.open_csv_file)
        menubar.add_cascade (label = 'Open CSV File', menu = open_file_menu)

        open_manager_manu = Menu(menubar, tearoff = 0)
        open_manager_manu.add_command( label = 'Open Graph Manager',
                                       command = lambda: self.raise_to_front('graph'))
        open_manager_manu.add_command( label = 'Open Sensor Manager',
                                       command = lambda: self.raise_to_front('manager'))

        menubar.add_cascade (label = 'Graph / Sensor', menu = open_manager_manu)

        Tk.config(self, menu = menubar)

        self.raise_to_front('graph')

    def raise_to_front(self, frame_name):
        if frame_name == 'graph':
            self.graph_page.tkraise()
        elif frame_name == 'manager':
            self.sensor_manager_page.tkraise()


    def open_csv_file(self):
        filename = str(askopenfilename(title = "Open File", filetypes = [('CSV','.csv')]))
        if len(filename) > 0 and not filename == '()':
            self.graph_page.file_path = filename

    def quit_application(self):
        self.sensor_manager_page.disconnect_all_sensors()
        self.quit()

    def run(self):
        self.geometry('1280x720')
        self.protocol("WM_DELETE_WINDOW", self.quit_application)

        self.graph_page.plot_points(stop_zoom_resetting = False)
        self.graph_page.graph_plot.set_xlim((-1,3000))
        self.graph_page.graph_plot.set_ylim((-1,5))
        anim = FuncAnimation(self.graph_page.graph_figure,
                             self.graph_page.plot_points,
                             interval = 1000)

        self.mainloop()




class Graph_Frame(Frame):
    def __init__(self, parent_container):

        Frame.__init__(self, parent_container)

        self.file_path = select_latest_file()

        self.graph_figure = Figure(figsize = (5,5), dpi = 100)
        self.graph_plot = self.graph_figure.add_subplot(1,1,1)

        # Setting up canvas
        self.canvas = FigureCanvasTkAgg(self.graph_figure, self)
        self.canvas.show()
        self.canvas._tkcanvas.pack(side = TOP, fill = BOTH, expand = True )

        # Setting up toolbar
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.toolbar.pack(side = BOTTOM, fill = BOTH, expand = False)

        self.points_to_plot = []


    def return_channel_color(self, channel):
        if channel == '64':
            line_color = 'b-'
            circle_color = 'bo'
        elif channel == '96':
            line_color = 'y-'
            circle_color = 'yo'
        else:
            line_color = 'r-'
            circle_color = 'ro'

        return (line_color, circle_color)

    def plot_points(self, i = 0, stop_zoom_resetting = True):

        if stop_zoom_resetting:
            x_axis_zoom = self.graph_plot.get_xlim()
            y_axis_zoom = self.graph_plot.get_ylim()

        if self.file_path[-len('Frequency.csv'):] == 'Frequency.csv':
            self.update_frequency_points()

        elif self.file_path[-len('Resistance.csv'):] == 'Resistance.csv':
            self.update_resistance_points()

        if stop_zoom_resetting:
            self.graph_plot.set_xlim(x_axis_zoom)
            self.graph_plot.set_ylim(y_axis_zoom)

    def update_frequency_points(self, i = 0):

        directory_of_channels = {'64':[ [], [] ], '96':[ [], [] ]}

        self.graph_plot.clear()

        with open(self.file_path, 'r') as current_file:
            file_lines = current_file.read().split('\n')

        time_duration_list = []
        frequency_list = []

        for line in list(file_lines):
            line = line.split(',')

            if len(line) < 3:
                continue
            if '\n' in line:
                line.remove('\n')
            if ' ' in line:
                line.remove(' ')
            if '' in line:
                line.remove('')
            for count in range(0, len(line), 3):

                line_color, circle_color = self.return_channel_color(line[count])

                directory_of_channels[line[count]][0].append(line[count + 1])
                directory_of_channels[line[count]][1].append(line[count + 2])


        for channel in directory_of_channels:
            line_color, circle_color = self.return_channel_color(channel)
            self.graph_plot.plot(directory_of_channels[channel][0],
                                 directory_of_channels[channel][1],
                                 line_color)
            self.graph_plot.plot(directory_of_channels[channel][0],
                                 directory_of_channels[channel][1],
                                 circle_color)

    def update_resistance_points(self):
        current_pos = 0
        self.graph_plot.clear()
        with open(self.file_path, 'r') as current_file:
            file_lines = current_file.read().split('\n')

        time_duration_list = []
        resistance_list = []

        for line in file_lines:
            if len(line) < 2:
                continue
            line = line.split(',')

            if '\n' in line:
                line.remove('\n')
            if '' in line:
                line.remove('')
            if ' ' in line:
                line.remove(' ')

            time_duration_list.append (line[0])
            resistance_list.append (line[3])

        self.graph_plot.plot(time_duration_list, resistance_list, 'g-')
        self.graph_plot.plot(time_duration_list, resistance_list, 'yo')

class Sensor_Manager_Frame(Frame):
    def __init__(self, parent_container):
        Frame.__init__(self, parent_container)

        self.scan_frame = Sensor_Scan_Frame(self)
        self.scan_frame.pack(side = TOP, fill = BOTH, expand = False)

        self.list_of_sensor_node_frames = []

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

        self.scan_button_frame = Frame(self)
        self.scan_list_frame = Frame(self)

        self.list_box = Listbox(self.scan_list_frame)
        self.scan_button = Button (self.scan_button_frame, text = 'Scan', command = self.scan_for_devices)
        self.add_sensor_node = Button (self.scan_button_frame, text = 'Add Sensor', command = self.add_sensor)

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
            self.scan_listbox.insert (END, 'Nothing Found')
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






if __name__ == '__main__':
    main_window = Main_Window()
    main_window.run()
