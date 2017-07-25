from main_window import *
import os

if not os.path.exists('sensor_data/'):
    os.mkdir('sensor_data/')

if __name__ == '__main__':

    app = QApplication(sys.argv)

    widget = Sensor_Manager_Widget()
    widget.show()

    sys.exit(app.exec_())
