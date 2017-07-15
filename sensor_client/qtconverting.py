from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QListWidget, QListWidgetItem, QLabel
from PyQt5.Qt import QThread



import sys

###############################################################################
# NOTE:
# TODO: WE SHOULD BE TARGETING JSON FORMATTING FOR OUTPUT
###############################################################################



class Sensor_Thread(QThread):
    def __init__(self, Sensor):
        pass

    def __del__(self):
        pass

    def run(self):
        pass

class Sensor_Frame(QWidget):
    def __init__(self, Sensor):
        super().__init__()

    def read_frequency(self):
        pass
    def read_resistance(self):
        pass
    def read_humidity(self):
        pass
    def read_pressure(self):
        pass




class Sensor_Manager_Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sensor Manager')

        self.list_widget = QListWidget(self)
        self.list_widget.show()

        list_to_add = ['a', 'b', 'c', 'd']
        self.add_list_to_listwidget(list_to_add)

    #TODO: Use HCITOOL CLASS TO LIST THE DEIVCES HERE
    def scan(self):
        pass
        
    def add_list_to_listwidget(self, list_to_add):
        self.list_widget.addItems(list_to_add)

    def show_widget(self):
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = Sensor_Manager_Widget()
    widget.show_widget()


    sys.exit(app.exec_())
