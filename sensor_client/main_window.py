from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QListWidget
from PyQt5.QtCore import QThread

from sensor import *

class Sensor_Control_Panel_Widget(QWidget):
    def __init__(self, parent_widget):
        QWidget.__init__(self, parent = parent_widget)

        self.vertical_box = QVBoxLayout()
        self.vertical_box.addStretch(1)

        self.list_of_sensor_widgets = []

        self.setLayout(self.vertical_box)

    def add_sensor(self, name, mac_address):
        for temp_sensor in self.list_of_sensor_widgets:
            if temp_sensor.mac_address == mac_address:
                return
        sensor = Sensor_Frame(self, name, mac_address)
        sensor.show()
        self.list_of_sensor_widgets.append(sensor)
        self.vertical_box.addWidget(sensor)

    def show_widget(self):
        self.show()

class Scan_Widget(QWidget):
    def __init__(self, parent_widget, sensor_control_panel):
        QWidget.__init__(self, parent = parent_widget)

        scanning_horizontal_box = QHBoxLayout()
        scanning_horizontal_box.addStretch(1)

        self.sensor_control_panel = sensor_control_panel

        self.list_widget = QListWidget(self)
        self.list_widget.show()

        self.scan_button = QPushButton('Scan', self)
        self.scan_button.clicked.connect(self.scan)
        self.scan_button.show()

        self.add_sensor_button = QPushButton('Add Sensor', self)
        self.add_sensor_button.clicked.connect(self.add_selected_sensor)
        self.add_sensor_button.show()

        scanning_horizontal_box.addWidget(self.list_widget)
        scanning_horizontal_box.addWidget(self.scan_button)
        scanning_horizontal_box.addWidget(self.add_sensor_button)

        self.setLayout(scanning_horizontal_box)


    def scan(self):
        list_of_devices = scan_for_nearby_ble_devices()
        self.list_widget.clear()

        for device in list_of_devices:
            text = '{}---{}'.format(device['name'], device['address'])
            self.list_widget.addItem(text)

    def add_selected_sensor(self):
        if self.list_widget.currentItem() is None:
            return
        line = self.list_widget.currentItem().text()
        name, address = line.split('---')

        self.sensor_control_panel.add_sensor(name, address)

    def show_widget(self):
        self.show()

class Sensor_Frame(QWidget):
    def __init__(self, parent_widget,  name, mac_address):
        QWidget.__init__(self, parent = parent_widget)

        self.name = name
        self.mac_address = mac_address
        self.sensor = Sensor(name, mac_address)
        self.sensor.start()

        self.name_label = QLabel(self.name, self)
        self.mac_address_label = QLabel(self.mac_address, self)

        self.name_label.show()
        self.mac_address_label.show()

        self.connect_button = QPushButton('Connect', self)
        self.read_frquency_button = QPushButton('Read Frequency', self)
        self.read_resistance_button = QPushButton('Read Resistance', self)
        self.read_temperature_button = QPushButton('Read Temperature', self)
        self.read_pressure_button = QPushButton('Read Pressure', self)
        self.read_humidity_button = QPushButton('Read Humidity', self)

        self.connect_button.setStyleSheet("background-color:rgb(255, 0, 0)")
        self.read_frquency_button.setStyleSheet("background-color:rgb(255, 0, 0)")
        self.read_resistance_button.setStyleSheet("background-color:rgb(255, 0, 0)")
        self.read_temperature_button.setStyleSheet("background-color:rgb(255, 0, 0)")
        self.read_pressure_button.setStyleSheet("background-color:rgb(255, 0, 0)")
        self.read_humidity_button.setStyleSheet("background-color:rgb(255, 0, 0)")

        self.read_frquency_button.clicked.connect(self.toogle_frequency)
        self.read_resistance_button.clicked.connect(self.toogle_resistance)
        self.read_temperature_button.clicked.connect(self.toogle_temperature)
        self.read_pressure_button.clicked.connect(self.toogle_pressure)
        self.read_humidity_button.clicked.connect(self.toogle_humidity)

        self.connect_button.show()
        self.read_frquency_button.show()
        self.read_resistance_button.show()
        self.read_temperature_button.show()
        self.read_pressure_button.show()
        self.read_humidity_button.show()

        horizontal_box = QHBoxLayout()
        horizontal_box.addWidget(self.name_label)
        horizontal_box.addWidget(self.mac_address_label)
        horizontal_box.addWidget(self.connect_button)
        horizontal_box.addWidget(self.read_frquency_button)
        horizontal_box.addWidget(self.read_resistance_button)
        horizontal_box.addWidget(self.read_temperature_button)
        horizontal_box.addWidget(self.read_pressure_button)
        horizontal_box.addWidget(self.read_humidity_button)

        self.setLayout(horizontal_box)


    def toogle_frequency(self):
        if self.sensor.record_frequency:
            self.sensor.record_frequency = False
            self.read_frquency_button.setStyleSheet("background-color:rgb(255, 0, 0)")
        else:
            self.sensor.record_frequency = True
            self.read_frquency_button.setStyleSheet("background-color:rgb(0, 255, 0)")


    def toogle_resistance(self):
        if self.sensor.record_resistance:
            self.sensor.record_resistance = False
            self.read_resistance_button.setStyleSheet("background-color:rgb(255, 0, 0)")
        else:
            self.sensor.record_resistance = True
            self.read_resistance_button.setStyleSheet("background-color:rgb(0, 255, 0)")

    def toogle_temperature(self):
        if self.sensor.record_temperature:
            self.sensor.record_temperature = False
            self.read_temperature_button.setStyleSheet("background-color:rgb(255, 0, 0)")
        else:
            self.sensor.record_temperature = True
            self.read_temperature_button.setStyleSheet("background-color:rgb(0, 255, 0)")

    def toogle_pressure(self):
        if self.sensor.record_pressure:
            self.sensor.record_pressure = False
            self.read_pressure_button.setStyleSheet("background-color:rgb(255, 0, 0)")
        else:
            self.sensor.record_pressure = True
            self.read_pressure_button.setStyleSheet("background-color:rgb(0, 255, 0)")

    def toogle_humidity(self):
        if self.sensor.record_humidity:
            self.sensor.record_humidity = False
            self.read_humidity_button.setStyleSheet("background-color:rgb(255, 0, 0)")
        else:
            self.sensor.record_humidity = True
            self.read_humidity_button.setStyleSheet("background-color:rgb(0, 255, 0)")

class Sensor_Manager_Widget(QWidget):
    def __init__(self):
        super().__init__()

        control_panel_widget = Sensor_Control_Panel_Widget(self)
        control_panel_widget.show()


        scan_widget = Scan_Widget(self, control_panel_widget)
        scan_widget.show()



        vertical_layout_box = QVBoxLayout()
        vertical_layout_box.addStretch(1)

        vertical_layout_box.addWidget(scan_widget)
        vertical_layout_box.addWidget(control_panel_widget)


        self.setLayout(vertical_layout_box)
