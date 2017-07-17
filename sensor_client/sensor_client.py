#######################################################################
# Writen by: Derek Santos
#######################################################################

"""
Hexadecimal Valued BLE Handle Codes:

0x02: HVPOT
0x03: LVPOT
0x04: IC
0x05: Gate Time
"""

#TODO: I THINK WHEN GATTOL FAILS IT DOES NOT LET SCANNING WORK



# Python Modules
import sys
import os
import struct
import binascii
from time import sleep, time, ctime
from threading import Thread

# 3rd Party Modules
from gattlib import DiscoveryService
import pexpect

# Developer Modules
from config import *

def ble_scan():
    # Scan's for all BLE devices nearby for 5 seconds
    try:
        service = DiscoveryService("hci0")
        nearby_devices = service.discover(2)
        return nearby_devices

    except RuntimeError as e:
        print('ERROR:', e)
        return None
    except Exception as e:
        print('ERROR: Exception:', e)

# Returns the voltage using the digital integer value
def get_voltage_out(digital_int_value, R2, ROFF):
    return 1.24 * (1 + (R2 / (dtap_to_rhvpot(digital_int_value) + ROFF) ) )

def dtap_to_rhvpot(digital_int_value):
    # Result is returned in Kili-Ohm
    return digital_int_value * (100 / 127)


class Sensor_Client():
    def __init__(self, ADDRESS):

        try:
            # Use spawnu in order to send commands as strings to stdout;
            # Pexpect sometimes sends with bytes using normal spawn()
            self.address = ADDRESS

            self.gtool = pexpect.spawnu('sudo gatttool -i hci0 -b {addr} -t random -I'.format(addr = self.address), timeout = 3)

            # PExpect logs will now output onto the screen
            #self.gtool.logfile = sys.stdout

            # Variable to check if we are connected to sensor
            self.connected = False

            # If this is set to True then if sensor is not connected, it will try to reconnect
            self.reconnecting_allowed = False

            # Variable that will be set to true when trying to connect to sensor.
            # Allows all other functions to be aware that we are trying to connect
            # to the sensor.
            self.stop_connection_checking = False

            # Variables to check if we are currently reading from sensor
            self.reading_frequency = False
            self.reading_resistance = False

            # Time variable to be used at the start of recording data
            self.start_time = None

            # Variable to be used when thread has stopped lopping
            self.is_stopped = False

            # All of the channels we will read
            self.channels = [0x00, 0x10,0x20,0x30,0x40,0x50,0x60,0x70]

            # Variable for the ammount of time gate time takes on the sensor
            # In milliseconds
            self.gate_time = 100 # milliseconds

            # Variable for the amout of time per bit
            time_per_bit = 1000 # in us

            self.reading_environment = False

            # Calculation for the total time we must request each frequency to be in sync with the sensor
            #self.time_per_bit_delay = time_per_bit * 4 * 8.0 * (1/1000000.0)

            # Default HV value being used at the start of recording data
            self.high_voltage = 0x50
            self.R2 = 1000
            self.ROFF = 50

            self.frequency_average = None
            self.frequency_list = []

            # Creation of the run thread
            self.run_thread = Thread(target=self.run, daemon = True, args=())
            self.run_thread.start()

        except Exception as e:
            raise e

    def change_address(self, address):
        self.address = address
        self.disconnect()
        self.gtool = pexpect.spawnu('sudo gatttool -i hci0 -b {addr} -t random -I'.format(addr = self.address), timeout = 3)

    # Function that attempts connection with the sensor
    # connect_one argument is if you only want to try to connect once
    def connect(self):
        # Since under __init__ has already spanwed the startup command
        # we can free-ly send the connect command to try to start a connection

        # Check's if connection is still alive before trying to connect again
        self.check_connection()
        if self.connected:
            return

        # If already connecting (possibily in another thread)
        if self.stop_connection_checking:
            return

        # While not connected then we must attempt connection until it connects again.
        start_connecting_attempt_time = time()

        # Sends the string 'connect' to gatttol
        self.gtool.sendline('connect')

        try:
            self.stop_connection_checking = True
            # If connection was successful we would get 'Connection successful' as output
            # If connection was unsuccessful we would try again.
            index = self.gtool.expect(['Connection successful',
                                       '.*busy.*',
                                       '.*Too many levels of symbolic links.*',
                                       '.*refused.*'], timeout = 3)
            if index == 0:
                self.connected = True
                #self.change_hv_value(self.high_voltage)
                self.stop_connection_checking = False
            elif index == 1:
                print ('Device busy. Trying again')
            elif index == 2:
                print ('Too many levels of symbolic links. Please restart device.')
                self.set_to_disconnected()
                return 'Too many symbolic links'
            elif index == 3:
                self.set_to_disconnected()
                #print ('Connection refused. Try again')

        # If pexpect time's out then set everything to disconnected and try again.
        except pexpect.exceptions.TIMEOUT as timeout:
            self.set_to_disconnected()
            #self.connect()

        except pexpect.exceptions.EOF as eof:
            self.gtool = pexpect.spawnu('sudo gatttool -i hci0 -b {addr} -t random -I'.format(addr = self.address), timeout = 3)
            #self.gtool.logfile = sys.stdout

        # If there was an uknown error state the error and try again.
        except Exception as e:
            print ('ERROR:', e)
            self.set_to_disconnected()



    # When the sensor disconnects, this function will update the class with the
    # correct data assignments
    def set_to_disconnected(self):
        self.connected = False
        #self.reading_frequency = False
        #self.stop_connection_checking = False

    # Changes the hv value if the sensor is connected
    def change_hv_value(self, value):

        # If not connected, print 'not connected', and return
        if not self.connected:
            print ('Not connected')
            return

        self.high_voltage = value

        # old reading channels value
        old_rc_value = self.reading_frequency

        # Stop attempting to read the values
        self.reading_frequency = False
        # Stop trying to see if the connection is still alive
        # (We already know it is)
        self.stop_connection_checking = True

        # Wait 3 seconds to make sure the reading thread has time to stop reading
        if self.reading_frequency or self.reading_resistance:
            sleep (3)
        # Send the command to gatttol in order to change the hv
        self.gtool.sendline(self.char_write(0x02, 0x00, self.high_voltage))
        # Sleep for 3 seconds to make sure the command was sent
        sleep(1/2)
        # Set reading_frequency to what it was before
        self.reading_frequency = old_rc_value
        # Check connection to make sure it is connected
        self.check_connection()
        # If not connected re-establish the connection
        # Changing high voltage using battery sometimes makes the sensor disconnect
        if self.connected == False:
            self.connect()
        # Continue to check if the connection is dropped
        self.stop_connection_checking = False

    def read_frequency(self):
        if self.start_time is None:
            self.start_time = time()

        # Each frequency that will be recorded will be put into this list.
        # The order of the frequencies will be respective to the order of the channels.
        frequencies = []
        # For each channel being passed into the class
        for channel in self.channels:
            # Ready the sensor for being used
            self.gtool.sendline(self.char_write(0x04, 0x80, channel + 0x80 + 0x0a))
            self.gtool.sendline(self.char_write(0x04, 0x80, channel + 0x80 + 0x0b))

            # Send the sensor the gate time desired
            self.gtool.sendline(self.gate_time_write(0x05, self.gate_time))

            # Sleep for the total time of the sensor's gate time
            #sleep(self.time_per_bit_delay)
            sleep(self.gate_time / 1000.0)

            # Request the frequency data
            self.gtool.sendline(self.char_write(0x04, 0x08, 0x04))
            #sleep(self.time_per_bit_delay)
            sleep(0.08)
            # To get the Frequency we have to take out the word 'descriptor' with the space at the end
            frequency = self.read_handle()
            if frequency is None:
                return
            frequency = frequency.replace(' ','')

            # Data transfered is little-edian. Convert the HEX to ASCII then INT
            count = struct.unpack('<I', binascii.unhexlify(frequency))[0]

            # Formula to convert the count recieved from Hz to MHz
            frequency = float(count) / float(2) / (self.gate_time / 1000.0) / 1000000.0
            frequencies.append((time() - self.start_time, frequency))

        file_name = '{0} - {1} - Frequency.csv'.format(self.address, ctime(self.start_time))
        file_name = file_name.replace(':', '_')
        with open(DIRECTORY_OF_SENSOR_DATA + file_name, 'a') as current_file:
            for channel, (time_dur, freq) in zip(self.channels, frequencies):
                data = '{0:02d},{1:5.1f},{2:1.8f},'.format(channel, time_dur, float (frequency))
                current_file.write(data)
            current_file.write('\n')

    def read_resistance(self):
        # If start_time was not initiated, the start_time is now
        if self.start_time is None:
            self.start_time = time()
        # Send command to get resistance
        self.gtool.sendline(self.char_write(0x04))
        sleep(0.1)
        # Read in the digital_value
        digital_value = self.read_handle()
        # Get the time_duration from when the voltage was recorded
        time_duration = time() - self.start_time

        if digital_value is None:
            return
        digital_value = digital_value.replace(' ', '')
        digital_value_hex = binascii.unhexlify(digital_value)
        digital_value = struct.unpack('<I', digital_value_hex)[0]

        # digital_value = Digital Value
        # vref = Voltage value
        #
        voltage_ref = 3.3
        vlsb = voltage_ref / 1023.0
        vlog = digital_value * vlsb
        vc = 5
        rl = 2.2
        # Calculate resistance
        resistance = (vc - vlog) * rl / vlog

        file_name = '{0} - {1} - {2}.csv'.format(self.address, ctime(self.start_time),'Resistance')
        file_name = file_name.replace(':', '_')
        with open(DIRECTORY_OF_SENSOR_DATA + file_name, 'a') as current_file:
            data = '{0:5.1f},{1:5d},{2:5.3f},{3:5.3f}\n'.format(time_duration, digital_value, voltage_ref, float(resistance))
            current_file.write(data)


    def read_temperature(self):
        if self.start_time is None:
            self.start_time = time()

        time_duration = time() - self.start_time
        self.gtool.sendline( self.char_write(6) )
        sleep(0.1)
        temp = self.read_handle()
        if temp is None:
            return
        temp = temp.replace(' ','')

        # Data transfered is little-edian. Convert the HEX to ASCII then INT
        temperature_float = struct.unpack('<f', binascii.unhexlify(temp))[0]

        return (time_duration, temperature_float)

        #file_name = '{0} - {1} - {2}.csv'.format(self.address, ctime(self.start_time),'Temperature')
        #file_name = file_name.replace(':','_')
        #with open(DIRECTORY_OF_SENSOR_DATA + file_name,'a') as current_file:
        #    current_file.write('{0:0.4f},{1:5.1f}\n'.format(time_duration, temperature_float))



    def read_pressure(self):
        if self.start_time is None:
            self.start_time = time()

        time_duration = time() - self.start_time
        self.gtool.sendline( self.char_write(7) )
        sleep(0.1)
        press = self.read_handle()
        if press is None:
            return
        press = press.replace(' ','')

        # Data transfered is little-edian. Convert the HEX to ASCII then INT
        pressure_float = struct.unpack('<f', binascii.unhexlify(press))[0]

        return (time_duration, pressure_float)

    def read_humidity(self):
        if self.start_time is None:
            self.start_time = time()

        time_duration = time() - self.start_time
        self.gtool.sendline( self.char_write(8) )
        sleep(0.1)
        humid = self.read_handle()
        if humid is None:
            return
        humid = humid.replace(' ','')

        # Data transfered is little-edian. Convert the HEX to ASCII then INT
        humidity_float = struct.unpack('<f', binascii.unhexlify(humid))[0]

        return (time_duration, humidity_float)

    # To calculate the frequency_average we take the average of frequency_list
    # But it will only do the latest 5 items
    def calculate_frequency_average(self):
        if len(self.frequency_list) > 5:
            self.frequency_list = self.frequency_list[len(self.frequency_list) - 5:]
        self.frequency_average = sum(self.frequency_list) / len(self.frequency_list)

    # This function will return True or False if the frequency is within the allowed range
    def check_frequency(self, frequency):
        self.calculate_frequency_average()
        lower_limit = float(self.frequency_average) - 0.2
        upper_limit = float(self.frequency_average) + 0.2
        return lower_limit <= frequency and frequency <= upper_limit

    # Python does not do function overloading
    def char_write(self, first_int, second_int = None, third_int = None):
        # Setting up general formatting of the char-write command using hex
        # Since python does not do function overloading we must 'overload' ourself
        if second_int is None and third_int is None:
            return 'char-write-cmd 0x0014 {0:02X}'.format(first_int)
        elif second_int != None and third_int is None:
            return 'char-write-cmd 0x0014 {0:02X}{1:02X}'.format(first_int, second_int)
        else:
            return 'char-write-cmd 0x0014 {0:02X}{1:02X}{2:02X}'.format(first_int, second_int, third_int)

    # General formatting of the gate time write command
    def gate_time_write(self, first_int, second_int):
        return 'char-write-cmd 0x0014 {0:02X}{1:04X}'.format(first_int, second_int)

    # General formating of the sensor's read command
    def read_handle(self):
        try:
            self.gtool.sendline('char-read-hnd 0x0011')
            value = self.gtool.expect(['descriptor: .*', '.*Disconnected.*','\'NoneType\' object is not subscriptable'])

            # Simple recusion just incase sensor disconnect
            # if returned value == 'descriptor .*' then return result
            # else it's disconnected; reconnect and try again
            if value == 0:
                if not self.gtool.after == '\'NoneType\' object is not subscriptable':
                    return self.gtool.after[len('descriptor: '):len('descriptor: ') + 11]
            elif value == 1:
                self.connect()
                self.read_handle()
            elif value == 2:
                pass

        except pexpect.exceptions.TIMEOUT as t:
            return

        except Exception as e:
            print ('ERROR:', e)

    # Checking connection by reading to the sensor
    # If descriptor is not sent back then assume disconnected
    def check_connection(self):
        try:
            self.gtool.sendline('char-read-hnd 0x0011')
            value = self.gtool.expect(['descriptor: .*', '.*Disconnected.*'])

            if value == 0:
                self.connected = True
            elif value == 1:
                self.connected = False
        except Exception as e:
            self.connected = False

    # The primary function to be multithreaded
    # This is the general flow for the progam
    def run(self):

        # While the sensor is being used
        while not self.is_stopped:
            try:
                if self.reading_frequency and self.connected:
                    # We must record the starting time that the sensor is being started
                    self.read_frequency()

                if self.reading_resistance and self.connected:
                    self.read_resistance()

                if self.reading_environment and self.connected:
                    temperature_tuple = self.read_temperature()
                    pressure_tuple = self.read_pressure()
                    humidity_tuple = self.read_humidity()

                    file_name = '{0} - {1} - {2}.csv'.format(self.address, ctime(self.start_time),'Environment')
                    file_name = file_name.replace(':','_')

                    with open(DIRECTORY_OF_SENSOR_DATA + file_name,'a') as current_file:
                        current_file.write('{0:5.4f},{1:1.8f},'.format(*temperature_tuple))
                        current_file.write('{0:5.4f},{1:5.2f},'.format(pressure_tuple[0],pressure_tuple[1]))
                        current_file.write('{0:5.4f},{1:5.2f}\n'.format(humidity_tuple[0], humidity_tuple[1]))

                if not self.stop_connection_checking and \
                     not self.reading_resistance and \
                     not self.reading_frequency and self.connected:
                    # To check if we are still connected we can read from the sensor
                    self.check_connection()
                    sleep (1)
                elif self.reconnecting_allowed and not self.connected:
                    self.connect()
                    sleep(3)
                else:
                    sleep (1)

            except Exception as e:
                print (e)

    def disconnect(self):
        self.set_to_disconnected()
        sleep(1)
        self.gtool.sendline('disconnect')
