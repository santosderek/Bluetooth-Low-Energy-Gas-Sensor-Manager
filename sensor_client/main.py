from main_window import *

if __name__ == '__main__':

    app = QApplication(sys.argv)

    widget = Sensor_Manager_Widget()
    widget.show()

    sys.exit(app.exec_())
