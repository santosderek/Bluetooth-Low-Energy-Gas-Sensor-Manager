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

        # Creating the container that will hold the graph
        self.graph_page = Graph_Page (main_frame, self.sensor_manager_page.sensor_collection_frame.list_of_sensor_node_frames)
        self.graph_page.grid (row = 0, column = 0, sticky = 'nsew')

        # Initializing Variables
        self.file_name = None

        # Creating the menu bar
        menubar = Menu(main_frame)

        # Creation of the Open File drop down
        open_file_menu = Menu(menubar, tearoff = 0)
        open_file_menu.add_command( label = 'Open Sensor File',
                                    command = self.open_csv_file)
        menubar.add_cascade (label = 'Open CSV File', menu = open_file_menu)

        # Creation of the Open Page drop down
        open_manager_menu = Menu(menubar, tearoff = 0)
        open_manager_menu.add_command( label = 'Open Graph Manager',
                                       command = lambda: self.raise_to_front('graph'))
        open_manager_menu.add_command( label = 'Open Sensor Manager',
                                       command = lambda: self.raise_to_front('manager'))
        menubar.add_cascade (label = 'Graph / Sensor', menu = open_manager_menu)

        # Creation of the Baseline drop down
        baseline_menu = Menu(menubar, tearoff = 0)
        baseline_menu.add_command( label = 'Change Baseline',
                                       command = self.open_baseline_child_window)

        menubar.add_cascade (label = 'Baseline', menu = baseline_menu)

        Tk.config(self, menu = menubar)
        self.raise_to_front('graph')

        # Creation of the object each thread will be put in
        self.graph_thread = None
        self.update_points_thread = None

    def open_baseline_child_window(self):
        pass

    # Raises the currently selected page to the top of the application
    def raise_to_front(self, frame_name):
        if frame_name == 'graph':
            self.graph_page.tkraise()
        elif frame_name == 'manager':
            self.sensor_manager_page.tkraise()

    # Opens any csv file created by the program.
    def open_csv_file(self):
        filename = str(askopenfilename(title = "Open File", filetypes = [('CSV','.csv')]))
        if len(filename) > 0 and not filename == '()':
            self.graph_page.file_path = filename
        self.graph_page.reset_labels = True

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

        self.graph_page.graph_frame.graph_plot.set_xlim((-1,3000))
        self.graph_page.graph_frame.graph_plot.set_ylim((-1,5))

        # Creation of the thread responsible for updating the points to graph
        self.update_points_thread = Thread(target=self.graph_page.graph_frame.update_points, args=(), daemon=True)
        self.update_points_thread.start()

        # Function that is used to update the graph using Blitting method
        anim = FuncAnimation(self.graph_page.graph_frame.graph_figure,
                             self.graph_page.graph_frame.plot_points,
                             interval = 1000,
                             frames = 1,
                             blit = True )

        self.mainloop()

if __name__ == '__main__':
    main_window = Main_Window()
    main_window.run()
