from main_window import *
import os


def main():
    if not os.path.exists('sensor_data/'):
        os.mkdir('sensor_data/')

    app = QApplication(sys.argv)

    widget = Sensor_Manager_Widget()
    widget.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
