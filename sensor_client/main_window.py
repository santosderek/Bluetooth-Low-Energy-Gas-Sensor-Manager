import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation


from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from graph_page import *
from sensor_page import *


from config import *



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

        open_manager_menu = Menu(menubar, tearoff = 0)
        open_manager_menu.add_command( label = 'Open Graph Manager',
                                       command = lambda: self.raise_to_front('graph'))
        open_manager_menu.add_command( label = 'Open Sensor Manager',
                                       command = lambda: self.raise_to_front('manager'))

        menubar.add_cascade (label = 'Graph / Sensor', menu = open_manager_menu)

        baseline_menu = Menu(menubar, tearoff = 0)
        baseline_menu.add_command( label = 'Change Baseline',
                                       command = self.open_baseline_child_window)

        menubar.add_cascade (label = 'Baseline', menu = baseline_menu)

        Tk.config(self, menu = menubar)

        self.raise_to_front('graph')

        self.graph_thread = None

    def open_baseline_child_window(self):
        pass

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
        self.sensor_manager_page.sensor_collection_frame.disconnect_all_sensors()
        self.quit()

    def run(self):
        self.geometry('1280x720')
        self.protocol("WM_DELETE_WINDOW", self.quit_application)

        #self.graph_page.plot_points(reset_zoom = False, loop = False)
        self.graph_page.graph_plot.set_xlim((-1,3000))
        self.graph_page.graph_plot.set_ylim((-1,5))
        anim = FuncAnimation(self.graph_page.graph_figure,
                             self.graph_page.plot_points,
                             interval = 500,
                             blit = True,
                             repeat = False)

        #self.graph_thread = Thread (target = self.graph_page.plot_points, args=(), daemon=True)
        #self.graph_thread.start()

        self.mainloop()

if __name__ == '__main__':
    main_window = Main_Window()
    main_window.run()
