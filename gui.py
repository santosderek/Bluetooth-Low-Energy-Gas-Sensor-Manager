import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

style.use('fivethirtyeight')

class Live_GUI():
    def __init__(self): 
        self.file_name = 'sensor_data/EA:13:A7:37:70:DE - Wed Jun  7 16:43:31 2017 - 64.csv'
        self.time_duration_list = []
        self.frequency_list = []
        self.figure = plt.figure()
        self.axis = self.figure.add_subplot(1,1,1)

    def plot_data(self, passedIn):
        with open(self.file_name,'r') as current_file:
            graph_data = current_file.read()

        lines = graph_data.split('\n')

        for line in lines:
            if len(line) > 1:
                time_duration, frequency = line.split(',')
                print (time_duration, frequency) 
                self.time_duration_list.append(time_duration)
                self.frequency_list.append(frequency)
         
        #axis.clear()
        self.axis.plot(self.time_duration_list, self.frequency_list)
        self.time_duration_list.clear()
        self.frequency_list.clear()

    def run(self):
        ani = animation.FuncAnimation(self.figure, self.plot_data, interval = 1000)
        plt.show()


if __name__ == '__main__':
    gui = Live_GUI()
    gui.run() 
