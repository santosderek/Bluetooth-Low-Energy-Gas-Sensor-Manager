import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.animation as animation
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk
import re
import os
from tkinter.filedialog import askopenfilename
from threading import Thread
# Dev Made Modules
from sensor_client import *

LARGE_FONT = ("Verdana", 12)
NORMAL_FONT = ("Verdana", 12)

def check_latest_modified_file(directory):
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


#######################################################################
# This will the container that we will put inside the main_frame
#######################################################################
class Graph_Container(tk.Frame):

    #######################################################################
    # Parent is the parent tk.Frame class when inherited
    # Controller is the class initialized that will use this Graph_Page
    #######################################################################
    def __init__(self, parent, controller, file_path):
        #######################################################################
        # Initalizing the Frame class's __init__ function
        #######################################################################
        tk.Frame.__init__(self, parent)

        #######################################################################
        # The file path of the .csv file that we will graph
        #######################################################################
        self.file_path = file_path

        #######################################################################
        # The list of frequencies that have been recorded
        #######################################################################
        self.frequency_list = []

        #######################################################################
        # Defining Figure and Plot classes to use with matplotlib's animation class
        #######################################################################
        self.graph_figure = Figure(figsize=(5,5), dpi=100)
        self.graph_plot = self.graph_figure.add_subplot(1,1,1)

        #######################################################################
        # Variables to set the graph's base zoom location
        # These corespond to the maximum x and y value the graph's plot has charted
        #######################################################################
        self.maximum_x_value = 0
        self.maximum_y_value = 0

        #######################################################################
        # Each Graph_Container will now consist of a sensor to keep track of
        #######################################################################
        self.sensor = Sensor_Client('')

        #######################################################################
        # Creating all overall outside frames used within controller
        #######################################################################

        # Frame that contains the graph
        self.graph_frame = tk.Frame(controller)
        # Frmae that contains the labels and buttons
        self.information_frame = tk.Frame(controller)
        # Frame that contains the Toolbar for the graph
        self.toolbar_frame = tk.Frame(controller)
        #######################################################################
        # Creating all the frames used in self.information_frame
        #######################################################################
        # Frame used to contain all the buttons within the information frame
        self.information_button_frame  = tk.Frame(self.information_frame)
        # Frame used to contain all the labels
        self.information_label_frame   = tk.Frame(self.information_frame)
        # Frame used for the listbox
        self.information_listbox_frame = tk.Frame(self.information_frame)

        #######################################################################
        # Creating the listbox used in self.information_listbox_frame
        #######################################################################
        self.scan_listbox = tk.Listbox(self.information_listbox_frame)
        self.scan_listbox.pack(side = tk.TOP, fill = tk.BOTH, expand = True)

        #######################################################################
        # Creating all the StringVar used in self.information_label_frame
        #######################################################################

        # Create a tk.StringVar to use for the label of the graph so we can control it
        self.sensor_connected_label = tk.StringVar()
        self.csv_file_name          = tk.StringVar()
        self.reading_frequency      = tk.StringVar()
        self.reading_resistance     = tk.StringVar()
        self.hv_value               = tk.StringVar()

        #######################################################################
        # Set each label's string to a default string
        #######################################################################
        self.change_file_path(self.file_path)
        self.sensor_connected_label.set('Sensor Connected: False')
        self.reading_frequency.set     ('Reading Frequency: False')
        self.reading_resistance.set    ('Reading Resistance: False')
        self.hv_value.set              ('HV Values: None')

        #######################################################################
        # Creating all the Labels used in self.information_label_frame
        #######################################################################

        csv_file_name_label = tk.Label(self.information_label_frame,
                                     textvariable = self.csv_file_name,
                                     font=NORMAL_FONT)
        connected_label = tk.Label(self.information_label_frame,
                                     textvariable = self.sensor_connected_label,
                                     font=NORMAL_FONT)
        reading_frequency_label = tk.Label(self.information_label_frame,
                                     textvariable = self.reading_frequency,
                                     font=NORMAL_FONT)
        reading_resistance_label = tk.Label(self.information_label_frame,
                                     textvariable = self.reading_resistance,
                                     font=NORMAL_FONT)
        hv_value_label = tk.Label(self.information_label_frame,
                                     textvariable = self.hv_value,
                                     font=NORMAL_FONT)

        #######################################################################
        # Packing all the Labels used in self.information_label_frame
        #######################################################################
        csv_file_name_label.pack      (pady=5, padx=5, side = tk.TOP)
        connected_label.pack          (pady=5, padx=5, side = tk.TOP)
        reading_frequency_label.pack  (pady=5, padx=5, side = tk.TOP)
        reading_resistance_label.pack (pady=5, padx=5, side = tk.TOP)
        hv_value_label.pack           (pady=5, padx=5, side = tk.TOP)

        #######################################################################
        # Creating all the Frames used in self.information_button_frame
        #######################################################################

        scan_frame = tk.Frame      (self.information_button_frame)
        connection_frame = tk.Frame(self.information_button_frame)
        read_frame = tk.Frame      (self.information_button_frame)
        file_buttons_frame = tk.Frame (self.information_button_frame)

        #######################################################################
        # Creating all the buttons used in self.information_button_frame
        #######################################################################

        # Creating the buttons and packing them instantly
        scan_button = ttk.Button(scan_frame,             text = 'Scan',            command = self.scan_for_devices)
        connect_button = ttk.Button(connection_frame,    text = 'Connect',         command = self.change_and_connect)
        disconnect_button = ttk.Button(connection_frame, text = 'Disconnect',      command = self.disconnect_sensor)
        read_frequency_button = ttk.Button(read_frame,   text = 'Read Frequency',  command = self.set_read_frequency_data)
        read_resistance_button = ttk.Button(read_frame,  text = 'Read Resistance', command = self.set_read_resistance_data)
        switch_to_latest_file_button = ttk.Button(file_buttons_frame, text = 'Change To Latest File', command = self.switch_file_to_latest)

        # Packing the buttons we created
        scan_button.pack  (side = tk.TOP,   fill = tk.BOTH, expand = True)
        connect_button.pack(side = tk.LEFT,  fill = tk.BOTH, expand = True)
        disconnect_button.pack (side = tk.RIGHT, fill = tk.BOTH, expand = True)
        read_frequency_button.pack(side = tk.LEFT,  fill = tk.BOTH, expand = True)
        read_resistance_button.pack(side = tk.RIGHT, fill = tk.BOTH, expand = True)
        switch_to_latest_file_button.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
        #######################################################################
        # Packing all the Frames used in self.information_button_frame
        #######################################################################
        read_frame.pack      (side = tk.BOTTOM, fill = tk.BOTH, expand = False)
        connection_frame.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = False)
        scan_frame.pack      (side = tk.BOTTOM, fill = tk.BOTH, expand = False)
        file_buttons_frame.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = False)

        #######################################################################
        # The canvas that will show the graph_figure in the window
        #######################################################################
        canvas = FigureCanvasTkAgg(self.graph_figure, self.graph_frame)
        canvas.show()

        #######################################################################
        # The toolbar that will show on the bottom of the window
        #######################################################################

        toolbar = NavigationToolbar2TkAgg(canvas, self.toolbar_frame)
        toolbar.update()

        #######################################################################
        # Packing the Toolbar
        #######################################################################
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        #######################################################################
        # Packing the Canvas
        #######################################################################
        canvas._tkcanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        #######################################################################
        # Packing all the Frames used in the overall Graph_Container
        #######################################################################
        # NOTE: The order of which thing's are packed is important
        self.toolbar_frame.pack    (side = tk.BOTTOM,fill = tk.BOTH, expand = False)
        self.graph_frame.pack      (side = tk.LEFT,  fill = tk.BOTH, expand = True)
        self.information_frame.pack(side = tk.RIGHT, fill = tk.BOTH, expand = False)

        #######################################################################
        # Packing all the Frames used within the information_frame
        #######################################################################
        self.information_listbox_frame.pack(side = tk.TOP,    fill = tk.BOTH, expand = True)
        self.information_label_frame.pack  (side = tk.TOP,    fill = tk.BOTH, expand = True)
        self.information_button_frame.pack (side = tk.BOTTOM, fill = tk.BOTH, expand = True)

        #######################################################################
        # Starting the Sensor's run thread
        # Also starting a thread to infinitely update the GUI's StringVar
        #######################################################################
        self.sensor_thread = Thread(target=self.sensor.run, args=())
        self.sensor_thread.daemon = True
        self.sensor_thread.start()

        self.sensor_label_thread = Thread(target=self.infinitely_change_sensor_labels, args=())
        self.sensor_label_thread.daemon = True
        self.sensor_label_thread.start()

        #######################################################################
        # Sets the graph's zoom variables to a default
        #######################################################################
        self.plot_frequency_data(None)
        #self.graph_plot.autoscale(enable = True)

        #######################################################################
        # Set the plots inital limits
        #######################################################################
        self.graph_plot.set_xlim((-1,300))
        self.graph_plot.set_ylim((-1,5))

        #######################################################################
        # Scan for inital devices
        #######################################################################
        self.scan_for_devices()


    #######################################################################
    # Sensor Manipulation Functions
    #######################################################################

    def scan_for_devices(self):
        scan_results = ble_scan()
        if scan_results is None:
            # Delete all items in listbox
            self.scan_listbox.delete(0, tk.END)
            self.scan_listbox.insert(tk.END, 'Nothing Found')
            return

        self.scan_listbox.delete(0, tk.END)
        for address, name in scan_results.items():
            self.scan_listbox.insert(tk.END, '{} - {}'.format(name, address))

    def set_read_frequency_data(self):
        if self.sensor.reading_frequency:
            self.sensor.reading_frequency = False
        else:
            self.sensor.reading_frequency = True


    def set_read_resistance_data(self):
        if self.sensor.reading_resistance:
            self.sensor.reading_resistance = False
        else:
            self.sensor.reading_resistance = True

    def change_and_connect(self):
        # Get selection from listbox
        selection = self.scan_listbox.get(self.scan_listbox.curselection())
        selection = re.search('\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2}', selection).group(0)

        # change the address of the pexpect class within Sensor_Client
        self.sensor.change_address(str(selection))

        # Connect to device
        returned_value = self.sensor.connect(True)

        if returned_value == 'Too many symbolic links':
            self.sensor_connected_label.set('ERROR: To Many Symbolic Links. Please Restart.')
            return

        #self.change_sensor_labels()

    def infinitely_change_sensor_labels(self):
        while (True):
            try:
                self.change_sensor_labels()
            except Exception as e:
                print ('ERROR - Sensor Labels:', e)

    def disconnect_sensor(self):
        self.sensor.disconnect()

    def change_sensor_labels(self):
        self.sensor_connected_label.set('Sensor Connected: %s' % self.sensor.connected)
        self.reading_frequency.set     ('Reading Frequency: %s' % self.sensor.reading_frequency)
        self.reading_resistance.set    ('Reading Resistance: %s' % self.sensor.reading_resistance)
        self.hv_value.set              ('HV Values: %s' % self.sensor.hv)

    #######################################################################
    # GUI Manipulation Functions
    #######################################################################

    def change_file_path(self, file_path):
        # Change the file path

        if file_path is None:
            self.csv_file_name.set('NO CSV File')
            self.file_path = None
            return

        self.file_path = file_path

        # Get the file name
        if self.file_path.find('/') != -1:
            text = self.file_path.split('/')
            text = text[len(text) - 1]
        elif self.file_path.find('\\') != -1:
            text = self.file_path.split('\\')
            text = text[len(text) - 1]
        else:
            text = self.file_path

        if text.count('-') == 3:
            label_contents = 'Sensor: {}\n\nTime: {}\n\nFile\'s channel:{}\n\nFile Type: {}'.format(*text.split('-'))
            self.csv_file_name.set(str(label_contents))
        else:
            self.csv_file_name.set('CSV Filename: ' + str(text))

        # Sets the graph's zoom variables to a default
        self.graph_plot.autoscale(enable = True)

        if self.file_path[-len('Resistance.csv'):] == 'Resistance.csv':
            self.plot_resistance_data(None)
        else:
            self.plot_frequency_data(None)

        self.graph_plot.set_xlim((-1, int(float(self.maximum_x_value))))
        self.graph_plot.set_ylim((-1, int(float(self.maximum_y_value))))

    def switch_file_to_latest(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        try:
            path_to_use = check_latest_modified_file(dir_path + '\sensor_data')
        except FileNotFoundError:
            path_to_use = check_latest_modified_file(dir_path + '/sensor_data')
        self.change_file_path(path_to_use)

    def plot_graph(self, i):
        if self.file_path[-len('Resistance.csv'):] == 'Resistance.csv':
            self.plot_resistance_data(0)

        elif self.file_path[-len('Resistance.csv'):] != 'Resistance.csv':
            self.plot_frequency_data(0)

    # Function that will be passed into the animation.FuncAnimation function
    # in order to plot the data in real time.
    def plot_frequency_data(self, i):
        # Opens the csv file that will be needed to plot the data
        if self.file_path is None:
            self.graph_plot.clear()
            return

        if self.file_path[-len('Resistance.csv'):] == 'Resistance.csv':
            return

        time_duration_list = []

        with open(self.file_path, 'r') as current_file:
            graph_data = current_file.read()

        # Splits the data into a list made of string elements
        lines = graph_data.split('\n')

        # Loops through each string element while spliting the element in order
        # to get each pair of time_duration and frequency
        for line in lines:
            if len(line) >= 1 and not re.search(r'^.*,.*$', line) is None:

                time_duration, frequency = line.split(',')
                time_duration_list.append(time_duration)
                self.frequency_list.append(frequency)

        # Saves the zoom dimensions of the graph since self.graph_plot.clear()
        # resets the dimensions within the function
        x_axis_zoom = self.graph_plot.get_xlim()
        y_axis_zoom = self.graph_plot.get_ylim()

        # Clear the plot and reset zoom settings
        self.graph_plot.clear()
        # Plot's the data into the current_plot class
        # First passed variable are the x-axis variables
        # Second passed variables are the y-axis variables
        # Each are list data types
        # Third passed variable is the color of the line and a '-' indicating it's a line
        # Then I create the same plots using scatter plot method to show the vertices.

        self.graph_plot.plot(time_duration_list, self.frequency_list, 'k-',
                             time_duration_list, self.frequency_list, 'bo')

        # Sets the graph's zoom variables to what the user had it to before
        self.graph_plot.set_xlim(x_axis_zoom)
        self.graph_plot.set_ylim(y_axis_zoom)

        self.maximum_x_value = time_duration_list.pop()
        converted_list = []
        self.maximum_y_value = 0
        for number in self.frequency_list:
            if float(number) > float(self.maximum_y_value):
                self.maximum_y_value = float(number) + 1

        # Clear each list to get read for the next set of data
        time_duration_list.clear()
        self.frequency_list.clear()

    def plot_resistance_data(self, i):
        # If file_path hasn't been set yet, clear graph and return
        if self.file_path is None:
            self.graph_plot.clear()
            return
        # if File_path has been set but is not a *Resistance.csv then return
        if self.file_path[-len('Resistance.csv'):] != 'Resistance.csv':
            return

        # Open self.file_path and read all the contents
        with open(self.file_path, 'r') as current_file:
            graph_data = current_file.read()

        # Split the contents into a list of lines
        lines = graph_data.split('\n')
        # Init the lists that we will use for plotting
        time_duration_list= []
        resistance_list = []
        # For each line, split the values and record them to be plotted later
        for line in lines:
            if len(line) > 1:
                line = line.replace (' ', '')
                time_duration, digital_value, voltage_ref, resistance = line.split(',')

                time_duration_list.append(time_duration)
                resistance_list.append(resistance)


        # Saves the zoom dimensions of the graph since self.graph_plot.clear()
        # resets the dimensions within the function
        x_axis_zoom = self.graph_plot.get_xlim()
        y_axis_zoom = self.graph_plot.get_ylim()

        # Clear the graph and then plot the points
        self.graph_plot.clear()
        self.graph_plot.plot(time_duration_list, resistance_list, 'k-',
                             time_duration_list, resistance_list, 'bo')

        # Sets the graph's zoom variables to what the user had it to before
        self.graph_plot.set_xlim(x_axis_zoom)
        self.graph_plot.set_ylim(y_axis_zoom)

        self.maximum_x_value = time_duration_list.pop()
        self.maximum_y_value = 0
        for number in resistance_list:
            if float(number) > self.maximum_y_value:
                self.maximum_y_value = float (number) + 1

        # Clear the points that we had before
        time_duration_list.clear()
        resistance_list.clear()
