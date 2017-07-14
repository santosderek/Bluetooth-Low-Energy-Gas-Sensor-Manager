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

# Developer Modules
from graph_page import *
from sensor_page import *
from config import *

# Base Tk class that will be used for the application
class Main_Window(Tk):

    def __init__(self, *args, **kwargs):
        # Initializing inherited Tk Class
        Tk.__init__(self, *args, **kwargs)
        Tk.wm_title(self, 'Live Sensor GUI')

        # Creation of a base frame to place the different pages onto
        main_frame = Frame(self)
        main_frame.pack( side = TOP, fill = BOTH, expand = True )
        main_frame.grid_rowconfigure(0, weight = 1 )
        main_frame.grid_columnconfigure(0, weight = 1 )

        #Creating the Sensor_Manager_Frame page
        self.sensor_manager_page = Sensor_Manager_Frame(main_frame)
        self.sensor_manager_page.grid (row = 0, column = 0, sticky = 'nsew')

        # Initializing Variables
        self.file_name = None

        # Creating the menu bar
        menubar = Menu(main_frame)

        # Creation of the Baseline drop down
        baseline_menu = Menu(menubar, tearoff = 0)
        baseline_menu.add_command(label = 'Change Baseline',
                                  command = self.open_baseline_child_window)

        menubar.add_cascade (label = 'Baseline', menu = baseline_menu)

        Tk.config(self, menu = menubar)
        self.raise_to_front('manager')

        # Creation of the object each thread will be put in
        self.update_points_thread = None

    def open_baseline_child_window(self):
        pass

    # Raises the currently selected page to the top of the application
    def raise_to_front(self, frame_name):
        if frame_name == 'manager':
            self.sensor_manager_page.tkraise()

    # Function that will be used to destroy all sensors before quitting the application
    def quit_application(self):
        self.sensor_manager_page.sensor_collection_frame.disconnect_all_sensors()
        self.quit()

    # The main function that will be used to start the Application
    def run(self):
        # Sets the Application to 720p
        self.geometry('1280x720')
        # Sets the 'quit_application' function to run before quitting the application
        self.protocol("WM_DELETE_WINDOW", self.quit_application)


        self.mainloop()

if __name__ == '__main__':
    main_window = Main_Window()
    main_window.run()
