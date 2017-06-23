import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from config import *

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
            line_color = 'g-'
            circle_color = 'go'
        elif channel == '16':
            line_color = 'y-'
            circle_color = 'yo'
        elif channel == '80':
            line_color = 'r-'
            circle_color = 'ro'
        elif channel == '32':
            line_color = 'm-'
            circle_color = 'mo'
        elif channel == '48':
            line_color = 'k-'
            circle_color = 'ko'
        elif channel == '112':
            line_color = 'c-'
            circle_color = 'co'
        else:
            line_color = 'r-'
            circle_color = 'ro'

        return (line_color, circle_color)

    def plot_points(self, i = 0, stop_zoom_resetting = True):

        if stop_zoom_resetting:
            x_axis_zoom = self.graph_plot.get_xlim()
            y_axis_zoom = self.graph_plot.get_ylim()

        self.graph_plot.clear()


        if self.file_path[-len('Frequency.csv'):] == 'Frequency.csv':
            self.update_frequency_points()

        elif self.file_path[-len('Resistance.csv'):] == 'Resistance.csv':
            self.update_resistance_points()

        handles, labels = self.graph_plot.get_legend_handles_labels()
        self.graph_plot.legend(handles, labels)


        if stop_zoom_resetting:
            self.graph_plot.set_xlim(x_axis_zoom)
            self.graph_plot.set_ylim(y_axis_zoom)

    def update_frequency_points(self, i = 0):

        directory_of_channels = {'64':[ [], [] ], '96':[ [], [] ], '16':[ [], [] ], '32':[ [], [] ], '48':[ [], [] ],'80':[ [], [] ],'112':[ [], [] ]}


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
                                 line_color,
                                 label = 'Channel %s' % str(channel))
            self.graph_plot.plot(directory_of_channels[channel][0],
                                 directory_of_channels[channel][1],
                                 circle_color,
                                 label = 'Channel %s' % str(channel))

    def update_resistance_points(self):
        current_pos = 0
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
