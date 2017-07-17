from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QListWidget,
                                QListWidgetItem, QLabel, QHBoxLayout, QVBoxLayout,
                                QGridLayout)
from PyQt5.Qt import QThread



import sys


from hcitool import *


from sensor_client import Sensor_Client
###############################################################################
# NOTE:
# TODO: WE SHOULD BE TARGETING JSON FORMATTING FOR OUTPUT
###############################################################################


class Sensor_Thread(QThread):
    def __init__(self, name, mac_address):
        QThread.__init__(self)
        self.name = name
        self.sensor = Sensor_Client(mac_address)

    def __del__(self):
        self.wait()

    def run(self):
        self.sensor.run()



class Scan_Widget(QWidget):
    def __init__(self, parent_widget, Sensor_Control_Panel_Widget = None):
        QWidget.__init__(self, parent = parent_widget)
        #self.sensor_control_panel_widget = Sensor_Control_Panel_Widget

        scanning_horizontal_box = QHBoxLayout()
        scanning_horizontal_box.addStretch(1)

        self.list_widget = QListWidget(self)
        self.list_widget.show()

        self.scan_button = QPushButton('Scan', self)
        self.scan_button.clicked.connect(self.scan)
        self.scan_button.show()

        self.add_sensor_button = QPushButton('Add Sensor', self)
        #self.add_sensor_button.clicked.connect(self.add_sensor_to_list)
        self.add_sensor_button.show()

        scanning_horizontal_box.addWidget(self.list_widget)
        scanning_horizontal_box.addWidget(self.scan_button)
        scanning_horizontal_box.addWidget(self.add_sensor_button)

        self.setLayout(scanning_horizontal_box)


    def scan(self):
        hcitool = HCITOOL()
        list_of_lines = hcitool.read_output()
        self.list_widget.addItems(list_of_lines[1:])

    def add_sensor_to_list(self):
        length_of_mac_address = len('XX:XX:XX:XX:XX:XX')
        sensor_line = str(self.list_widget.currentItem().text())
        sensor_mac_address = sensor_line[:length_of_mac_address]
        sensor_name = sensor_line[length_of_mac_address:]

        #self.sensor_control_panel_widget.add_sensor(sensor_name, sensor_mac_address)



    def show_widget(self):
        self.show()

class Sensor_Widget(QWidget):
    def __init__(self, parent_widget, sensor_name, sensor_mac_address):
        QWidget.__init__(self, parent_widget)

        #self.sensor_thread = Sensor_Thread(name = sensor_name, mac_address = sensor_mac_address)
        #self.sensor_thread.start()

        name_label = QLabel('', self)
        mac_address_label = QLabel('', self)
        reading_frequency_label = QLabel('Reading Frequency', self)
        reading_resistance_label = QLabel('Reading Resistance', self)
        reading_environment_label = QLabel('Reading Environment', self)

        name_label.show()
        mac_address_label.show()
        reading_frequency_label.show()
        reading_resistance_label.show()
        reading_environment_label.show()

        horizontal_box = QHBoxLayout()
        horizontal_box.addStretch(1)
        horizontal_box.addWidget(name_label)
        horizontal_box.addWidget(mac_address_label)
        horizontal_box.addWidget(reading_frequency_label)
        horizontal_box.addWidget(reading_resistance_label)
        horizontal_box.addWidget(reading_environment_label)

        self.setLayout(horizontal_box)

    def show_widget(self):

        self.show()

    def read_frequency(self):
        pass
    def read_resistance(self):
        pass
    def read_humidity(self):
        pass
    def read_pressure(self):
        pass

class Sensor_Control_Panel_Widget(QWidget):
    def __init__(self, parent_widget = None ):
        QWidget.__init__(self, parent_widget)

        self.vertical_box = QVBoxLayout()
        self.vertical_box.addStretch(1)

        self.list_of_sensor_widgets = []

        self.setLayout(self.vertical_box)

    def add_sensor(self, name, mac_address):
        sensor = Sensor_Widget(self, name, mac_address)
        sensor.show_widget()
        self.list_of_sensor_widgets.append(sensor)
        self.vertical_box.addWidget(sensor)




    def show_widget(self):
        self.show()

class Sensor_Manager_Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sensor Manager')
        self.setGeometry(100, 100, 1280, 720)

        #self.sensor_control_panel = Sensor_Control_Panel_Widget(self)
        #self.scan_widget = Scan_Widget(self)


        #self.scan_widget.show_widget()
        #self.sensor_control_panel.show_widget()

        #grid_layout = QGridLayout()
        #grid_layout.setSpacing(10)

        #grid_layout.addWidget(self.scan_widget, 1, 0 )
        #grid_layout.addWidget(self.sensor_control_panel, 2, 0 )

        #self.setLayout(grid_layout)

    def show_widget(self):
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = Sensor_Manager_Widget()
    widget.show_widget()


    sys.exit(app.exec_())
