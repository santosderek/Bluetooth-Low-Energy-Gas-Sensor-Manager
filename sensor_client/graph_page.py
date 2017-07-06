# 3rd Party Modules
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

# Python Modules
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from time import sleep, time
from queue import Queue
from threading import Thread

# Developer Modules
from config import *

###############################################################################
# Functions Related to Graph Page
###############################################################################

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

###############################################################################
# Classes Related to Graph Page
###############################################################################

class Graph_Page(Frame):
    def __init__(self, parent_container, list_of_sensor_node_frames):

        Frame.__init__(self, parent_container)

        self.parent_container = parent_container



        self.graph_frame = Graph_Frame(self)
        self.graph_frame.pack(side = TOP, fill = BOTH, expand = True)

        # Creation of the checkbox frame.
        # This frame will allow the user to start and stop the drawing of any
        # line, using their channel number.
        self.graph_checkbox_frame = Channel_Checkbox_Frame(self)
        self.graph_checkbox_frame.pack(side = TOP, fill = BOTH, expand = False)

        # Creation of the settings Frame.
        # This allows the user to change the X and Y ranges of the graph on the fly.
        self.graph_settings_frame = Graph_Settings_Frame(self)
        self.graph_settings_frame.pack(side = LEFT, fill = BOTH, expand = True)

        # This is a frame responsible for voltage control of the specified sensor
        self.voltage_control_frame = Voltage_Control_Frame(self, list_of_sensor_node_frames)
        self.voltage_control_frame.pack(side = RIGHT, fill = BOTH, expand = True)

class Graph_Frame(Frame):
    def __init__(self, parent_container):
        Frame.__init__(self, parent_container)

        self.graph_figure = Figure(figsize = (1,1), dpi = 100)
        self.graph_plot = self.graph_figure.add_subplot(1,1,1)

        self.file_path = select_latest_file()
        self.parent_container = parent_container

        # Setting up canvas
        self.canvas = FigureCanvasTkAgg(self.graph_figure, self)
        self.canvas._tkcanvas.pack(side = TOP, fill = BOTH, expand = True )
        self.canvas.show()

        # Setting up toolbar
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.toolbar.pack(side = BOTTOM, fill = BOTH, expand = False)

        self.points_to_plot = []

        # This variable allows the developer to update the graph's axis' and
        # legend at will.
        self.reset_labels = True

        # This variable keep the time of when the graph has been cleared. Doing
        # so will allow the developer to clear the graph when there has been
        # too many points drawn.
        self.last_time_cleared = time()

        # A Queue that can be used to transport data between threads safely.
        self.queue = Queue(3)

        self.graph_title = ''
        self.graph_y_axis_label = ''
        self.graph_x_axis_label = ''

        self.graph_lines = []

        self.graph_figure.canvas.mpl_connect('draw_event', self.update_background)

        self.directory_of_channels = {0: [ [], [] ],
                                      16:[ [], [] ],
                                      32:[ [], [] ],
                                      48:[ [], [] ],
                                      64:[ [], [] ],
                                      80:[ [], [] ],
                                      96:[ [], [] ],
                                      112:[ [], [] ]}


    # Function that will be used to update the points to be used for the graph
    def update_points(self):

        while True:
            try:
                # If the Queue is full then we should not do unnessesary plotting
                if self.queue.full() or self.file_path is None:
                    sleep(1/2)
                    continue

                # If the current file that we are plotting is a frequency csv
                # Then we must use the update frequency function
                elif self.file_path[-len('Frequency.csv'):] == 'Frequency.csv':
                    lines = self.update_frequency_points()

                # If the current file that we are plotting is a resistance csv
                # Then we must use the update resistance function
                elif self.file_path[-len('Resistance.csv'):] == 'Resistance.csv':
                    lines = self.update_resistance_points()

                self.queue.put(lines)
            except Exception as e:
                print ('ERROR: Update Points:', e)

    def plot_points(self, i = 0):
        try:

            # Recorded the limits of the grpah in order to prevent resetting when
            # the graph is cleared.
            x_axis_zoom = self.graph_plot.get_xlim()
            y_axis_zoom = self.graph_plot.get_ylim()

            # Clears the graph every 2 seconds in order to keep memory to not increase.
            # I have noticed that if this is not done then memory will continously increase.
            # Since, the points are possibily being drawn ontop of each other.
            if time() - self.last_time_cleared >= 2:
                self.graph_plot.clear()
                self.last_time_cleared = time()
                self.reset_labels = True

            # When true, resets the axis and legend labels
            if self.reset_labels:
                self.refresh_labels()

            # When there is data within the queue we can get the data in order.
            if not self.queue.empty():
                self.graph_lines = self.queue.get()
            # Else we must clear the plot. If this is not done then there is a
            # chance that junkdata will be plotted.
            # Lastly, The last points that have been plotted will be plotted agian.
            else:
                self.graph_plot.clear()
                self.refresh_labels()


            # TODO: need to make a checkbox that can toogle this on and off
            # Automatically shifts the graph along with the data points
            x_left, x_right = x_axis_zoom
            x_left  += 1
            x_right += 1

            # Set the limits
            self.graph_plot.set_xlim((x_left, x_right))
            self.graph_plot.set_ylim(y_axis_zoom)

            #self.graph_figure.canvas.restore_region(self._background)


            return self.graph_lines

        except Exception as e:
            print ('ERROR: Plot Points:', e)

    def update_background(self, event):
        self._background = self.graph_figure.canvas.copy_from_bbox(self.graph_plot.bbox)

    def refresh_labels(self):
        legend_handles, legend_labels = self.graph_plot.get_legend_handles_labels()
        self.graph_plot.legend(legend_handles, legend_labels)

        self.graph_plot.grid(b=True, which = 'both')


        if not self.file_path is None:
            mac_address = re.search(r'\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2}', self.file_path).group(0)
            start_time = re.search(r'\w{3}\s\w{3}\s{1,2}\d{1,2}\s\d{2}:\d{2}:\d{2}\s\d{4}', self.file_path).group(0)
        else:
            mac_address = ''
            start_time = ''

        if self.file_path is None:
            self.graph_figure.suptitle('No File Selected', fontsize=11)

        elif self.file_path[-len('Frequency.csv'):] == 'Frequency.csv':
            self.graph_title = 'Resonant frequency\n{}\n{}'.format(mac_address, start_time)
            self.graph_y_axis_label = 'Frequency (MHz)'
            self.graph_x_axis_label = 'Time Duration (Seconds)'

        elif self.file_path[-len('Resistance.csv'):] == 'Resistance.csv':
            self.graph_title = 'Resistance\n{}\n{}'.format(mac_address, start_time)
            self.graph_y_axis_label ='Resistance'
            self.graph_x_axis_label = 'Time Duration (Seconds)'

        self.graph_figure.suptitle(self.graph_title, fontsize=11)
        self.graph_plot.set_ylabel(self.graph_y_axis_label)
        self.graph_plot.set_xlabel(self.graph_x_axis_label)

        self.reset_labels = False

    def update_frequency_points(self, i = 0):

        for key in self.directory_of_channels.keys():
            self.directory_of_channels[key][0].clear()
            self.directory_of_channels[key][1].clear()

        lines = []

        with open(self.file_path, 'r') as current_file:
            file_lines = current_file.read().split('\n')

        for each_line in file_lines:
            each_line = each_line.split(',')

            if len(each_line) < 3:
                continue
            for element in ['\n', ' ', '']:
                if element in each_line:
                    each_line.remove(element)

            for count in range(0, len(each_line), 3):
                channel_number = int(each_line[count])
                self.directory_of_channels[channel_number][0].append(each_line[count + 1])
                self.directory_of_channels[channel_number][1].append(each_line[count + 2])

        for number, channel in enumerate( sorted(self.directory_of_channels.keys()) ):
            if self.parent_container.graph_checkbox_frame.directory_of_channels[channel].get() == 0:
                continue

            lines.append ( self.graph_plot.plot(self.directory_of_channels[channel][0],
                                 self.directory_of_channels[channel][1],
                                 LINE_COLORS[number],
                                 animated = True,
                                 marker = 'o',
                                 linestyle = '-',
                                 label = 'Channel %s' % number)[0] )
        return lines

    def update_resistance_points(self):
        with open(self.file_path, 'r') as current_file:
            file_lines = current_file.read().split('\n')

        time_duration_list = []
        resistance_list = []

        lines = []

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

        lines.append( self.graph_plot.plot(time_duration_list,
                             resistance_list,
                             LINE_COLORS[0],
                             marker = 'o',
                             linestyle = '-',
                             label = 'Resistance')[0] )

        return lines


class Graph_Settings_Frame (Frame):
    def __init__ (self, parent_container):
        Frame.__init__ (self, parent_container)

        self.parent_container = parent_container

        Label(self, text = 'Graph Settings').pack(side = TOP, fill = BOTH, expand = True)

        ###############################################################
        # X RANGE
        self.x_range_frame = Frame(self)

        self.x_left_intvar = IntVar()
        self.x_right_intvar = IntVar()
        self.y_left_intvar = IntVar()
        self.y_right_intvar = IntVar()

        self.x_left_intvar.set(0)
        self.x_right_intvar.set(3000)
        self.y_left_intvar.set(0)
        self.y_right_intvar.set(5)

        self.x_left_intvar.trace('w', lambda name, index, mode, sv=self.x_left_intvar: self.update_graph_limits())
        self.x_right_intvar.trace('w', lambda name, index, mode, sv=self.x_right_intvar: self.update_graph_limits())
        self.y_left_intvar.trace('w', lambda name, index, mode, sv=self.y_left_intvar: self.update_graph_limits())
        self.y_right_intvar.trace('w', lambda name, index, mode, sv=self.y_right_intvar: self.update_graph_limits())

        Label(self.x_range_frame, text = 'X Range:').pack(side = LEFT, fill = BOTH, expand = False)

        self.x_left_limit_entry  = Entry(self.x_range_frame, textvariable = self.x_left_intvar, validate='focusout', validatecommand=self.update_graph_limits)
        self.x_right_limit_entry = Entry(self.x_range_frame, textvariable = self.x_right_intvar, validate='focusout', validatecommand=self.update_graph_limits)

        self.x_left_limit_entry.pack (side = LEFT, fill = BOTH, expand = True)
        self.x_right_limit_entry.pack(side = RIGHT, fill = BOTH, expand = True)

        self.x_range_frame.pack(side = TOP, fill = BOTH, expand = True)
        ###############################################################

        ###############################################################
        # Y RANGE
        self.y_range_frame = Frame(self)

        Label(self.y_range_frame, text = 'Y Range:').pack(side = LEFT, fill = BOTH, expand = False)

        self.y_left_limit_entry  = Entry(self.y_range_frame, textvariable = self.y_left_intvar, validate='focusout', validatecommand=self.update_graph_limits)
        self.y_right_limit_entry = Entry(self.y_range_frame, textvariable = self.y_right_intvar, validate='focusout', validatecommand=self.update_graph_limits)

        self.y_left_limit_entry.pack (side = LEFT,  fill = BOTH, expand = True)
        self.y_right_limit_entry.pack(side = RIGHT, fill = BOTH, expand = True)

        self.y_range_frame.pack(side = TOP, fill = BOTH, expand = True)

        ###############################################################

        self.change_button = Button (self, text = 'Apply Limits', command = self.update_graph_limits)
        self.change_button.pack (side = BOTTOM, fill = BOTH, expand = True)

    def update_graph_limits(self):
        # Convert text into int: X Left Limit
        try:
            x_left_int = self.x_left_intvar.get()
        except Exception as e:
            x_left_int = self.parent_container.graph_plot.get_xlim()[0]

        # Convert text into int: X Right Limit
        try:
            x_right_int = self.x_right_intvar.get()

        except Exception as e:
            x_right_int = self.parent_container.graph_plot.get_xlim()[1]

        # Convert text into int: Y Left Limit
        try:
            y_left_int = self.y_left_intvar.get()

        except Exception as e:
            y_left_int = self.parent_container.graph_plot.get_ylim()[0]

        # Convert text into int: Y Right Limit
        try:
            y_right_int = self.x_right_intvar.get()

        except Exception as e:
            y_right_int = self.parent_container.graph_plot.get_ylim()[1]

        # Now set the graph to these limits
        self.parent_container.graph_frame.graph_plot.set_ylim((y_left_int, y_right_int))
        self.parent_container.graph_frame.graph_plot.set_xlim((x_left_int, x_right_int))

class Channel_Checkbox_Frame(Frame):
    def __init__(self, parent_container):
        Frame.__init__(self, parent_container)

        self.parent_container = parent_container

        self.directory_of_channels = {0: IntVar(),
                                      16:IntVar(),
                                      32:IntVar(),
                                      48:IntVar(),
                                      64:IntVar(),
                                      80:IntVar(),
                                      96:IntVar(),
                                      112:IntVar()}

        Label(self, text = 'Channel Checkboxes').pack(side = TOP, fill = BOTH, expand = True)

        # Create checkbox based on sorted directory of channels keys
        sorted_directory_of_channels_keys = sorted(self.directory_of_channels.keys())
        for number, channel in enumerate(sorted_directory_of_channels_keys):
            box = Checkbutton(self, text = str(number), variable = self.directory_of_channels[channel])
            self.directory_of_channels[channel].set(1)
            box.pack(side = LEFT, fill = BOTH, expand = True)


class Voltage_Control_Frame(Frame):
    def __init__(self, parent_container, list_of_sensor_node_frames):
        Frame.__init__(self, parent_container)

        self.parent_container = parent_container

        self.list_of_sensor_node_frames = list_of_sensor_node_frames

        list_of_mac_addresses = []
        for frame in self.list_of_sensor_node_frames:
            list_of_mac_addresses.append(frame.sensor.address)

        self.list_frame    = Frame(self)
        self.voltage_frame = Frame(self)
        self.r2_frame      = Frame(self)
        self.roff_frame    = Frame(self)
        self.apply_frame   = Frame(self)

        self.current_sensor_name = StringVar()
        self.current_sensor_name.set('Devices')

        self.voltage_label_stringvar = StringVar()
        self.voltage_label_stringvar.set('Voltage: None')

        # Creation
        self.sensor_list_menu = OptionMenu(self.list_frame, self.current_sensor_name, *list_of_mac_addresses)
        self.r2_entry = Entry (self.r2_frame)
        self.roff_entry = Entry (self.roff_frame)
        self.voltage_label = Label(self.voltage_frame, textvariable = self.voltage_label_stringvar)

        self.apply_button = Button(self.apply_frame, text = 'Apply')

        # Packing labels & Buttons
        Label(self, text = 'Voltage Settings').pack(side = TOP, fill = BOTH, expand = True)
        self.sensor_list_menu.pack(side = TOP, fill = BOTH, expand = True)

        self.voltage_label.pack(side = LEFT, fill = BOTH, expand = True )

        Label(self.r2_frame, text = 'R2').pack(side = LEFT, fill = BOTH, expand = True)
        self.r2_entry.pack(side = RIGHT, fill = BOTH, expand = True)

        Label(self.roff_frame, text = 'ROFF').pack(side = LEFT, fill = BOTH, expand = True)
        self.roff_entry.pack(side = RIGHT, fill = BOTH, expand = True)

        self.apply_button.pack(side = TOP, fill = BOTH, expand = True)

        # Packing Frames
        self.list_frame.pack(side = TOP, fill = BOTH, expand = TRUE)
        self.voltage_frame.pack(side = TOP, fill = BOTH, expand = TRUE)
        self.r2_frame.pack(side = TOP, fill = BOTH, expand = TRUE)
        self.roff_frame.pack(side = TOP, fill = BOTH, expand = TRUE)
        self.apply_frame.pack(side = TOP, fill = BOTH, expand = TRUE)


    def check_device_settings(self, mac_address):
        pass


    def update_voltage_label(self, voltage_int):
        text = 'Voltage: ' + str(voltage_int)
        self.voltage_label_stringvar.set(text)
