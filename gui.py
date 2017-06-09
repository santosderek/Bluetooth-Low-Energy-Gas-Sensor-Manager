import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation

LARGE_FONT= ("Verdana", 12)

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

        # Initializing the Graph_Container class which contains the graph that will be shown on screen
        self.graph_frame = Graph_Container(main_frame, self, "sensor_data/temp.csv")
        self.graph_frame.grid(row=0, column=0, sticky="nsew")
        self.graph_frame.tkraise()

    def run(self):
        figure_animation = animation.FuncAnimation(self.graph_frame.graph_figure, self.graph_frame.plot_figure, interval = 1000)
        self.mainloop()


class Graph_Container(tk.Frame):

    # Parent is the parent tk.Frame class when inherited
    # Controller is the class initialized that will use this Graph_Page
    def __init__(self, parent, controller, file_path):
        self.file_path = file_path
        self.time_duration_list = []
        self.frequency_list = []

        # Defining Figure and Plot classes to use with matplotlib's animation class
        self.graph_figure = Figure(figsize=(5,5), dpi=100)
        self.graph_plot = self.graph_figure.add_subplot(1,1,1)

        # Initalizing the Frame class's __init__ function 
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Sensor", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

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

    # Function that will be passed into the animation.FuncAnimation function
    # in order to plot the data in real time.
    def plot_figure(self, i):
        # Opens the csv file that will be needed to plot the data
        with open(self.file_path, 'r') as current_file:
            graph_data = current_file.read()

        # Splits the data into a list made of string elements
        lines = graph_data.split('\n')

        # Loops through each string element while spliting the element in order
        # to get each pair of time_duration and frequency
        for line in lines:
            if len(line) > 1:
                time_duration, frequency = line.split(',')
                self.time_duration_list.append(time_duration)
                self.frequency_list.append(frequency)

        # Plot's the data into the current_plot class
        # First passed variable are the x-axis variables
        # Second passed variables are the y-axis variables
        # Each are list data types
        self.graph_plot.plot(self.time_duration_list, self.frequency_list)

        # Clear each list to get read for the next set of data
        self.time_duration_list.clear()
        self.frequency_list.clear()

if __name__ == '__main__':
    app = Live_GUI()
    app.run()
