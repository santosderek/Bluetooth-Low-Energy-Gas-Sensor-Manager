import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.animation as animation
from matplotlib.figure import Figure
matplotlib.use("TkAgg")
import tkinter as tk
from tkinter import ttk
import re
import os
from tkinter.filedialog import askopenfilename

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

class Live_GUI(tk.Tk):

    def __init__(self, *args, **kwargs):

        # Initializing tk window and title
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Live Sensor GUI")

        # Main frame where graphs and the such will be drawn
        main_frame = tk.Frame(self)
        main_frame.pack(side="top", fill="both", expand = True)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Getting the latest file
        dir_path = os.path.dirname(os.path.realpath(__file__))

        try:
            file_to_use = check_latest_modified_file(dir_path + '\sensor_data')
        except FileNotFoundError:
            file_to_use = check_latest_modified_file(dir_path + '/sensor_data')
        # Initializing the Graph_Container class which contains the graph that will be shown on screen
        self.graph_frame = Graph_Container(main_frame, self, file_to_use)
        self.graph_frame.grid(row=0, column=0, sticky="nsew")
        self.graph_frame.tkraise()

        # Init Menu bar
        menubar = tk.Menu(main_frame)
        sensor_file_menu = tk.Menu(menubar, tearoff = 0)
        sensor_file_menu.add_command(label = 'Open Sensor File', command = self.open_sensor_file )
        menubar.add_cascade (label = 'File', menu = sensor_file_menu)

        tk.Tk.config(self, menu = menubar)

    def open_sensor_file(self):
        filename = str(askopenfilename(title = "Open File", filetypes = [('CSV','.csv')]))
        if len(filename) > 0:
            self.graph_frame.change_file_path(filename)

    def run(self):
        figure_animation = animation.FuncAnimation(self.graph_frame.graph_figure, self.graph_frame.plot_figure, interval = 1000)
        self.mainloop()

# This will the container that we will put inside the main_frame
class Graph_Container(tk.Frame):

    # Parent is the parent tk.Frame class when inherited
    # Controller is the class initialized that will use this Graph_Page
    def __init__(self, parent, controller, file_path):
        self.file_path = file_path
        self.time_duration_list = []
        self.frequency_list = []
        self.lines = None

        # Defining Figure and Plot classes to use with matplotlib's animation class
        self.graph_figure = Figure(figsize=(5,5), dpi=100)
        self.graph_plot = self.graph_figure.add_subplot(1,1,1)

        # Initalizing the Frame class's __init__ function
        tk.Frame.__init__(self, parent)

        # Create a tk.StringVar to use for the label of the graph so we can control it
        self.sensor_name = tk.StringVar()
        # Set the label to the file_path we already have
        self.change_file_path(self.file_path)

        # Create the Label using self.sensor_name
        sensor_name_label = tk.Label(self, textvariable=self.sensor_name, font=LARGE_FONT)
        sensor_name_label.pack(pady=10,padx=5)

        # The canvas that will show the graph_figure in the window
        canvas = FigureCanvasTkAgg(self.graph_figure, self)
        # Write it on screen
        canvas.show()
        # Fill the graph to the whole screen
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Responsible for giving the toolbar on the bottom of the window
        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Sets the graph's zoom variables to a default
        self.plot_figure(None)
        #self.graph_plot.autoscale(enable = True)

        self.graph_plot.set_xlim((-1,300))
        self.graph_plot.set_ylim((-1,2))


    def change_file_path(self, file_path):
        # Change the file path


        if file_path is None:
            self.sensor_name.set('No Sensor')
            self.file_path = None
            return

        self.file_path = file_path

        # Change what the label says
        if self.file_path.find('/') != -1:
            text = self.file_path.split('/')
            text = text[len(text) - 1]
        elif self.file_path.find('\\') != -1:
            text = self.file_path.split('\\')
            text = text[len(text) - 1]
        else:
            text = self.file_path
        self.sensor_name.set(str(text))

        # Sets the graph's zoom variables to a default
        self.graph_plot.autoscale(enable = True)
        self.plot_figure(None)

    # Function that will be passed into the animation.FuncAnimation function
    # in order to plot the data in real time.
    def plot_figure(self, i):
        # Opens the csv file that will be needed to plot the data
        if self.file_path is None:
            self.graph_plot.clear()
            return

        with open(self.file_path, 'r') as current_file:
            graph_data = current_file.read()

        # Splits the data into a list made of string elements
        self.lines = graph_data.split('\n')

        # Loops through each string element while spliting the element in order
        # to get each pair of time_duration and frequency
        for line in self.lines:
            if len(line) >= 1 and not re.search(r'^.*,.*$', line) is None:

                time_duration, frequency = line.split(',')
                self.time_duration_list.append(time_duration)
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

        self.graph_plot.plot(self.time_duration_list, self.frequency_list, 'k-',
                             self.time_duration_list, self.frequency_list, 'bo')

        # Sets the graph's zoom variables to what the user had it to before
        self.graph_plot.set_xlim(x_axis_zoom)
        self.graph_plot.set_ylim(y_axis_zoom)

        # Clear each list to get read for the next set of data
        self.time_duration_list.clear()
        self.frequency_list.clear()



if __name__ == '__main__':
    app = Live_GUI()
    app.geometry('1280x720')
    app.run()
