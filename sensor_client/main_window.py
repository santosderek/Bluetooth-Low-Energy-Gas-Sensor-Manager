from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QFormLayout, QLineEdit, QDialog, QGridLayout
from PyQt5.QtGui import QIntValidator

from sensor import *

class Sensor_Control_Panel_Widget(QWidget):
    def __init__(self, parent_widget):
        QWidget.__init__(self, parent = parent_widget)

        self.list_of_sensor_widgets = []

        self.vertical_box = QVBoxLayout()
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


class Settings_Widget(QDialog):
    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget

        # Gate Time Control
        self.gate_time_line_edit = QLineEdit(self)
        self.gate_time_line_edit.setValidator(QIntValidator())
        gate_time_string = str(self.parent_widget.sensor.gate_time)
        self.gate_time_line_edit.setText(gate_time_string)
        self.gate_time_line_edit.textChanged.connect(self.gate_time_changed)

        # Voltage Control
        self.voltage_label = QLabel('', self)
        voltage_string = str(self.parent_widget.sensor.convert_voltage())
        self.voltage_label.setText(voltage_string)
        self.voltage_line_edit = QLineEdit(self)
        self.voltage_line_edit.setValidator(QIntValidator())
        self.voltage_line_edit.setText(str(self.parent_widget.sensor.voltage))
        self.voltage_line_edit.textChanged.connect(self.voltage_changed)

        self.voltage_confirm_button = QPushButton('Confirm Voltage', self)
        self.voltage_confirm_button.clicked.connect(self.change_voltage)

        # Channel Toggle Buttons
        self.channel_one_toogle_button   = QPushButton('Toogle', self)
        self.channel_two_toogle_button   = QPushButton('Toogle', self)
        self.channel_three_toogle_button = QPushButton('Toogle', self)
        self.channel_four_toogle_button  = QPushButton('Toogle', self)
        self.channel_five_toogle_button  = QPushButton('Toogle', self)
        self.channel_six_toogle_button   = QPushButton('Toogle', self)
        self.channel_seven_toogle_button = QPushButton('Toogle', self)
        self.channel_eight_toogle_button = QPushButton('Toogle', self)

        self.channel_one_toogle_button.clicked.connect(self.toogle_channel_one)
        self.channel_two_toogle_button.clicked.connect(self.toogle_channel_two)
        self.channel_three_toogle_button.clicked.connect(self.toogle_channel_three)
        self.channel_four_toogle_button.clicked.connect(self.toogle_channel_four)
        self.channel_five_toogle_button.clicked.connect(self.toogle_channel_five)
        self.channel_six_toogle_button.clicked.connect(self.toogle_channel_six)
        self.channel_seven_toogle_button.clicked.connect(self.toogle_channel_seven)
        self.channel_eight_toogle_button.clicked.connect(self.toogle_channel_eight)

        self.channel_one_toogle_button.setStyleSheet("color:rgb(0, 255, 0)")
        self.channel_two_toogle_button.setStyleSheet("color:rgb(0, 255, 0)")
        self.channel_three_toogle_button.setStyleSheet("color:rgb(0, 255, 0)")
        self.channel_four_toogle_button.setStyleSheet("color:rgb(0, 255, 0)")
        self.channel_five_toogle_button.setStyleSheet("color:rgb(0, 255, 0)")
        self.channel_six_toogle_button.setStyleSheet("color:rgb(0, 255, 0)")
        self.channel_seven_toogle_button.setStyleSheet("color:rgb(0, 255, 0)")
        self.channel_eight_toogle_button.setStyleSheet("color:rgb(0, 255, 0)")

        self.channel_one_toogle_button.show()
        self.channel_two_toogle_button.show()
        self.channel_three_toogle_button.show()
        self.channel_four_toogle_button.show()
        self.channel_five_toogle_button.show()
        self.channel_six_toogle_button.show()
        self.channel_seven_toogle_button.show()
        self.channel_eight_toogle_button.show()

        self.voltage_label.show()
        self.gate_time_line_edit.show()
        self.voltage_line_edit.show()
        self.voltage_confirm_button.show()

        form_layout = QFormLayout()
        form_layout.addRow('Gate Time (ms)', self.gate_time_line_edit)
        form_layout.addRow('Voltage (Ohms)', self.voltage_label)
        form_layout.addRow('Set Voltage (hex-to-int)', self.voltage_line_edit)
        form_layout.addRow('Confirm Voltage', self.voltage_confirm_button)
        form_layout.addRow('Channel One',   self.channel_one_toogle_button)
        form_layout.addRow('Channel Two',   self.channel_two_toogle_button)
        form_layout.addRow('Channel Three', self.channel_three_toogle_button)
        form_layout.addRow('Channel Four',  self.channel_four_toogle_button)
        form_layout.addRow('Channel Five',  self.channel_five_toogle_button)
        form_layout.addRow('Channel Six',   self.channel_six_toogle_button)
        form_layout.addRow('Channel Seven', self.channel_seven_toogle_button)
        form_layout.addRow('Channel Eight', self.channel_eight_toogle_button)

        self.setLayout(form_layout)

        self.show()

    def toogle_channel_one(self):
        ACTIVE_CHANNEL_LIST[0] = not ACTIVE_CHANNEL_LIST[0]

        if ACTIVE_CHANNEL_LIST[0]:
            self.channel_one_toogle_button.setStyleSheet("color:rgb(0, 255, 0)")
        else:
            self.channel_one_toogle_button.setStyleSheet("color:rgb(255, 0, 0)")


    def toogle_channel_two(self):
        ACTIVE_CHANNEL_LIST[1] = not ACTIVE_CHANNEL_LIST[1]

        if ACTIVE_CHANNEL_LIST[1]:
            self.channel_two_toogle_button.setStyleSheet("color:rgb(0, 255, 0)")
        else:
            self.channel_two_toogle_button.setStyleSheet("color:rgb(255, 0, 0)")

    def toogle_channel_three(self):
        ACTIVE_CHANNEL_LIST[2] = not ACTIVE_CHANNEL_LIST[2]

        if ACTIVE_CHANNEL_LIST[2]:
            self.channel_three_toogle_button.setStyleSheet("color:rgb(0, 255, 0)")
        else:
            self.channel_three_toogle_button.setStyleSheet("color:rgb(255, 0, 0)")

    def toogle_channel_four(self):
        ACTIVE_CHANNEL_LIST[3] = not ACTIVE_CHANNEL_LIST[3]

        if ACTIVE_CHANNEL_LIST[3]:
            self.channel_four_toogle_button.setStyleSheet("color:rgb(0, 255, 0)")
        else:
            self.channel_four_toogle_button.setStyleSheet("color:rgb(255, 0, 0)")

    def toogle_channel_five(self):
        ACTIVE_CHANNEL_LIST[4] = not ACTIVE_CHANNEL_LIST[4]

        if ACTIVE_CHANNEL_LIST[4]:
            self.channel_five_toogle_button.setStyleSheet("color:rgb(0, 255, 0)")
        else:
            self.channel_five_toogle_button.setStyleSheet("color:rgb(255, 0, 0)")

    def toogle_channel_six(self):
        ACTIVE_CHANNEL_LIST[5] = not ACTIVE_CHANNEL_LIST[5]

        if ACTIVE_CHANNEL_LIST[5]:
            self.channel_six_toogle_button.setStyleSheet("color:rgb(0, 255, 0)")
        else:
            self.channel_six_toogle_button.setStyleSheet("color:rgb(255, 0, 0)")

    def toogle_channel_seven(self):
        ACTIVE_CHANNEL_LIST[6] = not ACTIVE_CHANNEL_LIST[6]

        if ACTIVE_CHANNEL_LIST[6]:
            self.channel_seven_toogle_button.setStyleSheet("color:rgb(0, 255, 0)")
        else:
            self.channel_seven_toogle_button.setStyleSheet("color:rgb(255, 0, 0)")

    def toogle_channel_eight(self):
        ACTIVE_CHANNEL_LIST[7] = not ACTIVE_CHANNEL_LIST[7]

        if ACTIVE_CHANNEL_LIST[7]:
            self.channel_eight_toogle_button.setStyleSheet("color:rgb(0, 255, 0)")
        else:
            self.channel_eight_toogle_button.setStyleSheet("color:rgb(255, 0, 0)")


    def gate_time_changed(self, value):
        if value == '':
            return
        self.parent_widget.sensor.gate_time = int(value)

    def voltage_changed(self, value):
        if value == '':
            return

        voltage = get_voltage_out(float(value),
                                  self.parent_widget.sensor.R2,
                                  self.parent_widget.sensor.ROFF)
        self.voltage_label.setText(str(voltage))

    def change_voltage(self):
        self.parent_widget.sensor.change_voltage(int(self.voltage_line_edit.text()))


class Scan_Widget(QWidget):
    def __init__(self, parent_widget, sensor_control_panel):
        QWidget.__init__(self, parent = parent_widget)

        scanning_horizontal_box = QHBoxLayout()

        self.sensor_control_panel = sensor_control_panel

        self.list_widget = QListWidget(self)
        self.list_widget.show()

        self.scan_button = QPushButton('Scan', self)
        self.scan_button.clicked.connect(self.scan)
        self.scan_button.show()

        self.add_sensor_button = QPushButton('Add Sensor', self)
        self.add_sensor_button.clicked.connect(self.add_selected_sensor)
        self.add_sensor_button.show()

        button_layout = QVBoxLayout()
        self.scan_button.setMinimumSize(200, 350)
        self.add_sensor_button.setMinimumSize(200, 350)
        button_layout.addWidget(self.scan_button)
        button_layout.addWidget(self.add_sensor_button)

        # The second argument is the order of intensity to stretch the widget
        scanning_horizontal_box.addWidget(self.list_widget)
        scanning_horizontal_box.addLayout(button_layout)

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
        self.settings_button = QPushButton('Settings', self)

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
        self.settings_button.clicked.connect(self.open_popup_settings)

        self.connect_button.show()
        self.read_frquency_button.show()
        self.read_resistance_button.show()
        self.read_temperature_button.show()
        self.read_pressure_button.show()
        self.read_humidity_button.show()
        self.settings_button.show()

        horizontal_box = QHBoxLayout()
        horizontal_box.addWidget(self.name_label)
        horizontal_box.addWidget(self.mac_address_label)
        horizontal_box.addWidget(self.connect_button)
        horizontal_box.addWidget(self.read_frquency_button)
        horizontal_box.addWidget(self.read_resistance_button)
        horizontal_box.addWidget(self.read_temperature_button)
        horizontal_box.addWidget(self.read_pressure_button)
        horizontal_box.addWidget(self.read_humidity_button)
        horizontal_box.addWidget(self.settings_button)

        self.setLayout(horizontal_box)
        self.popup_settings = None

    def open_popup_settings(self):
        self.popup_settings = Settings_Widget(self)

    def toogle_frequency(self):
        self.sensor.record_frequency = not self.sensor.record_frequency

        if self.sensor.record_frequency:
            self.read_frquency_button.setStyleSheet("background-color:rgb(255, 0, 0)")
        else:
            self.read_frquency_button.setStyleSheet("background-color:rgb(0, 255, 0)")

    def toogle_resistance(self):
        self.sensor.record_resistance = not self.sensor.record_resistance
        if self.sensor.record_resistance:
            self.read_resistance_button.setStyleSheet("background-color:rgb(255, 0, 0)")
        else:
            self.read_resistance_button.setStyleSheet("background-color:rgb(0, 255, 0)")

    def toogle_temperature(self):
        self.sensor.record_temperature = not self.sensor.record_temperature

        if self.sensor.record_temperature:
            self.read_temperature_button.setStyleSheet("background-color:rgb(255, 0, 0)")
        else:
            self.read_temperature_button.setStyleSheet("background-color:rgb(0, 255, 0)")

    def toogle_pressure(self):
        self.sensor.record_pressure = not self.sensor.record_pressure

        if self.sensor.record_pressure:
            self.read_pressure_button.setStyleSheet("background-color:rgb(255, 0, 0)")
        else:
            self.read_pressure_button.setStyleSheet("background-color:rgb(0, 255, 0)")

    def toogle_humidity(self):
        self.sensor.record_humidity = not self.sensor.record_humidity

        if self.sensor.record_humidity:
            self.read_humidity_button.setStyleSheet("background-color:rgb(255, 0, 0)")
        else:
            self.read_humidity_button.setStyleSheet("background-color:rgb(0, 255, 0)")


class Sensor_Manager_Widget(QWidget):
    def __init__(self):
        super().__init__()

        control_panel_widget = Sensor_Control_Panel_Widget(self)
        control_panel_widget.show()

        scan_widget = Scan_Widget(self, control_panel_widget)
        scan_widget.show()

        vertical_layout_box = QVBoxLayout()

        vertical_layout_box.addWidget(scan_widget)
        vertical_layout_box.addWidget(control_panel_widget)

        self.setLayout(vertical_layout_box)
        self.setGeometry(100, 100, 1280, 720)
