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

# Dev Made Modules
from sensor_client import *
from graph_container import *

class Live_GUI(tk.Tk):

    def __init__(self, *args, **kwargs):

        # Initializing tk window and title
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Live Sensor GUI")

        # Main frame where graphs and the such will be drawn
        main_frame = tk.Frame(self)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand = False)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Getting the latest file
        dir_path = os.path.dirname(os.path.realpath(__file__))

        try:
            path_to_use = check_latest_modified_file(dir_path + '\sensor_data')
        except FileNotFoundError:
            path_to_use = check_latest_modified_file(dir_path + '/sensor_data')
        # Initializing the Graph_Container class which contains the graph that will be shown on screen
        self.graph_frame = Graph_Container(main_frame, self, path_to_use)
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
        if len(filename) > 0 and not filename == '()':
            self.graph_frame.change_file_path(filename)

    def close_program(self):
        self.graph_frame.sensor.disconnect()
        self.quit()

    def run(self):
        figure_animation = animation.FuncAnimation(self.graph_frame.graph_figure, self.graph_frame.plot_graph, interval = 1000)
        self.mainloop()

if __name__ == '__main__':
    app = Live_GUI()
    app.geometry('1280x720')
    app.protocol("WM_DELETE_WINDOW", app.close_program)
    app.run()
