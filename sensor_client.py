"""

Hexadecimal values:

0x02: HVPOT
0x03: LVPOT
0x04: IC
0x05: Gate Time



"""

import pexpect
import sys
import struct
import binascii
from time import sleep, time 


class Sensor_Client(): 
    def __init__(self, ADDRESS): 
        
        try:
            # Use spawnu in order to send commands as strings to stdout;
            # Pexpect sometimes sends with bytes using normal spawn()
            self.address = ADDRESS
            
            self.gtool = pexpect.spawnu('sudo gatttool -i hci0 -b {addr} -t random -I'.format(addr = self.address))     
            
            # PExpect logs will now output onto the screen
            #self.gtool.logfile = sys.stdout

            # Variable to check if we are connected to sensor
            self.connected = False

            # Variable to check if we are currently reading from sensor
            self.reading_channels = False

            # Time variable to be used at the start of recording data
            self.start_time = None

            # Variable to be used when thread has stopped lopping
            self.is_stopped = False 

            # All of the channels we will read
            self.channels = [0x40, 0x60]

            # Variable for the ammount of time gate time takes on the sensor
            # In milliseconds
            self.gate_time = 100 # milliseconds

            # Variable for the amout of time per bit
            self.time_per_bit = 1000 # in us

            # Calculation for the total time we must request each frequency to be in sync with the sensor
            self.gate_time_delay = self.time_per_bit * 4 * 8.0 * (1/1000000.0)

            # Default HV value being used at the start of recording data
            self.hv = 0x60

            # Attempt connection to sensor
            self.connect()
            if self.connected:
                self.change_hv_value(self.hv)
            
        except Exception as e:
            raise e
        
    def connect(self):
        # Since under __init__ has already spanwed the startup command
        # we can free-ly send the connect command to try to start a connection
        self.gtool.sendline('connect')

        try:
            # This line will jump one line down
            #index = self.gtool.expect('\n')
            
            # If connection was successful we would get 'Connection successful' as output
            # If connection was unsuccessful we would try again. 
            index = self.gtool.expect(['Connection successful',
                                       'Error: connect: Device or resource busy.*',
                                       '.*Too many levels of symbolic links.*'])
            if index == 0:
                self.connected = True
            elif index == 1:
                self.connect()
            elif index == 2:
                print ('Too many levels of symbolic links. Please restart device.')
            
        except pexpect.exceptions.TIMEOUT as timeout:
            print ('Request Timed out. Please try again.')           
            self.connected = False

        except Exception as e:
            print ('ERROR:', e)
            self.connected = False
            

    def change_hv_value(self, value):
        self.hv = value
        old_state = self.reading_channels 
        self.reading_channels = False
        
        sleep (3)
        self.gtool.sendline(self.char_write(0x02, 0x00, self.hv))
        sleep(2)
        
        self.reading_channels = old_state

    def request_frequency(self):
        # We must record the starting time that the sensor is being started
        
        self.start_time = time()

        # While the sensor is being used
        while not self.is_stopped:
            try:
                if (self.reading_channels and self.connected):
                    # For each channel being passed into the class
                    for channel in self.channels:
                        # Ready the sensor for being used
                        self.gtool.sendline(self.char_write(0x04, 0x80 + 0x00, channel + 0x80 + 0x0a))
                        self.gtool.sendline(self.char_write(0x04, 0x80 + 0x00, channel + 0x80 + 0x0b))

                        # Send the sensor the gate time desired
                        self.gtool.sendline(self.gate_time_write(0x05, self.gate_time))

                        # Sleep for the total time of the sensor's gate time
                        sleep(self.gate_time_delay)
                        sleep(self.gate_time / 1000.0)

                        # Request the frequency data
                        self.gtool.sendline(self.char_write(0x04, 0x08, 0x04))
                        sleep(self.gate_time_delay)

                        # To get the Frequency we have to take out the word 'descriptor' with the space at the end
                        frequency = self.read_handle()[len('descriptor: '):len('descriptor: ') + 11]
                        frequency = frequency.replace(' ','')

                        # Data transfered is little-edian. Convert the HEX to ASCII then INT
                        count = struct.unpack('<I', binascii.unhexlify(frequency))[0]

                        # Formula to convert the count recieved from Hz to MHz
                        frequency = float(count) / float(2) / (self.gate_time / 1000.0) / 1000000.0

                        # Append this value and the current time duration to a file
                        with open('{0} - osc_drift_ch_{1:02d}.csv'.format(self.address, channel), 'a') as current_file:
                            data = '{0:5.1f},{1:1.8f}\n'.format(time() - self.start_time, float (frequency))
                            current_file.write(data)
            except Exception as e:
                print (e) 

        self.reading_channels = False
                
    
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
            value = self.gtool.expect(['descriptor: .*', '.*Disconnected.*'])

            # Simple recusion just incase sensor disconnect
            # if returned value == 'descriptor .*' then return result
            # else it's disconnected; reconnect and try again
            if value == 0:
                return self.gtool.after
            elif value == 1:
                self.connect()
                self.read_handle()

        except pexpect.exceptions.TIMEOUT:
            print ('Reading timed out.')
        except Exception as e:
            print ('ERROR:', e)
            
    def disconnect(self):
        self.is_stopped = True
        self.gtool.sendline('exit')
        

    # The primary function to be multithreaded
    # This is the general flow for the progam
    def run(self):
        self.request_frequency()
    
 
