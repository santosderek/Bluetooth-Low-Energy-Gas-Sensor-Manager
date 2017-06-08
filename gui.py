import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

style.use('fivethirtyeight')

figure = plt.figure()
axis = figure.add_subplot(1,1,1)

def animate(passedIn):
     
    graph_data = None
    with open('EA:13:A7:37:70:DE - Wed Jun  7 16:43:31 2017 - 96.csv') as current_file:
        graph_data = current_file.read() 
    

    lines = graph_data.split('\n')

    time_duration_list = []
    frequency_list = []

    for line in lines:
        if len(line) > 1:
            time_duration, frequency = line.split(',')
            time_duration_list.append(time_duration)
            frequency_list.append(frequency)


    #axis.clear()
    axis.plot(time_duration_list, frequency_list)
    

ani = animation.FuncAnimation(figure, animate, interval = 1000)
plt.show() 
    
