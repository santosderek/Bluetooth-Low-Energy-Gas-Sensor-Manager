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
from time import sleep, time, ctime 


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

            self.attempting_to_connect = False

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
            self.hv = 0x50

            # Attempt connection to sensor
            #self.connect()
            #if self.connected:
            #    self.change_hv_value(self.hv)
            
        except Exception as e:
            raise e
        
    def connect(self):
        # Since under __init__ has already spanwed the startup command
        # we can free-ly send the connect command to try to start a connection
        self.check_connection()
        if self.connected:
            return
        
        self.gtool.sendline('connect')
        self.connected = False

        try:
            self.attempting_to_connect = True
            # If connection was successful we would get 'Connection successful' as output
            # If connection was unsuccessful we would try again. 
            index = self.gtool.expect(['Connection successful',
                                       '.*busy.*',
                                       '.*Too many levels of symbolic links.*',
                                       '.*Connection refused.*'])
            if index == 0:
                self.connected = True
                #self.change_hv_value(self.hv) 
                self.attempting_to_connect = False
                
            elif index == 1:
                print ('Device busy. Trying again') 
                self.connect() 
            elif index == 2:
                print ('Too many levels of symbolic links. Please restart device.')
                self.set_to_disconnected() 
            elif index == 3:
                self.set_to_disconnected() 
                print ('Connection refused. Try again')
            
        except pexpect.exceptions.TIMEOUT as timeout:           
            self.set_to_disconnected()
            self.connect()

        except Exception as e:
            print ('ERROR:', e)
            self.set_to_disconnected() 

    def set_to_disconnected(self):
        self.connected = False
        self.reading_channels = False
        self.attempting_to_connect = False
            

    def change_hv_value(self, value):
        self.hv = value
        
        if not self.connected:
            print ('Not connected')
            return
        # old reading channels value 
        old_rc_value = self.reading_channels
        self.reading_channels = False
        self.attempting_to_connect = True
        
        sleep (3)
        #print (self.char_write(0x02, 0x00, self.hv)    )
        self.gtool.sendline(self.char_write(0x02, 0x00, self.hv))
        sleep(3)

        self.reading_channels = old_rc_value
        self.check_connection()
        if self.connected == False:
            self.connect()
        self.attempting_to_connect = False

    def request_frequency(self):
        

        # While the sensor is being used
        while not self.is_stopped:
            try:
                if self.reading_channels and self.connected:
                    # We must record the starting time that the sensor is being started
                    if self.start_time is None:
                        self.start_time = time()
                    # For each channel being passed into the class
                    for channel in self.channels:
                        # Ready the sensor for being used
                        self.gtool.sendline(self.char_write(0x04, 0x80, channel + 0x80 + 0x0a))
                        self.gtool.sendline(self.char_write(0x04, 0x80, channel + 0x80 + 0x0b))

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
                        # The file name contains the MAC Address, Date/time, and channel
                        with open('{0} - {1} - {2:02d}.csv'.format(self.address, ctime(self.start_time), channel), 'a') as current_file:
                            data = '{0:5.1f},{1:1.8f}\n'.format(time() - self.start_time, float (frequency))
                            current_file.write(data)
    
                elif (not self.attempting_to_connect) and (self.connected):
                    # To check if we are still connected we can read from the sensor
                    self.check_connection() 
                    
            except Exception as e:
                #print (e)
                pass

        
                
    
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
                    return self.gtool.after
            elif value == 1: 
                self.connect()
                self.read_handle()
            elif value == 2:
                pass 

        except pexpect.exceptions.TIMEOUT as t:
            pass
            
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
            
    def disconnect(self):
        self.is_stopped = True
        self.gtool.sendline('exit')
        

    # The primary function to be multithreaded
    # This is the general flow for the progam
    def run(self):
        self.request_frequency()
    
 
