from sensor_manager import *
from sensor_client import *
from time import sleep
import re




def main():
    # In house "temp" sensor manager
    main_loop_running = True
    device_manager = Sensor_Manager()
    print ('For help type \'help\'')

    while (main_loop_running):

        command = str(input('> '))
        command_list = command.split(' ')
        first_word = command_list[0]

        try:
            if first_word == 'help':
                print ('list')
                print ('scan')
                print ('connect', '[sensor #]')
                print ('add', '[mac_address]')
                print ('remove', '[sensor_number]')
                print ('frequency_start', '[device #]')
                print ('resistance_start', '[device #]')
                print ('stop', '[device #]')
                print ('start_all')
                print ('stop_all')
                print ('hv', '[sensor #]', '[value]')
                print ('exit')

            elif first_word == 'list':
                device_manager.list_devices()

            elif first_word == 'scan':
                ble_scan()

            elif first_word =='add' and len(command.split()) >= 2:
                print ('Adding Device')
                mac_address = re.search('\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2}', command_list[1])
                if not mac_address is None:
                    device_manager.add_device(mac_address.group(0))

            elif first_word == 'connect':
                print ('Connecting to sensor')
                device_manager.connect_device(int(command_list[1]) - 1)

            elif first_word == 'remove':
                print ('Removing Device')
                device_manager.remove_device(int(command_list[1]) - 1 )

            elif first_word == 'frequency_start':
                print ('Starting Frequency Retrieval')
                device_manager.start_device_frequency(int(command_list[1]) - 1)

            elif first_word == 'resistance_start':
                print ('Starting Resistance Retrieval')
                device_manager.start_device_resistance(int(command_list[1]) - 1)

            elif first_word == 'stop':
                print ('Stopping device')
                device_manager.stop_device_frequency(int(command_list[1]) - 1)
                device_manager.stop_device_resistance(int(command_list[1]) - 1)
            #elif first_word == 'start_all':
            #    print ('Starting all Devices')
            #    device_manager.start_all_devices()

            elif first_word == 'stop_all':
                print ('Stopping All Devices')
                device_manager.stop_all_devices()

            elif first_word == 'hv':
                print ('Setting HV Value')
                value = command.split()[2]
                if value[:2] != '0x':
                    value = '0x' + value

                device_manager.change_hv_value(int(command_list[1]) - 1, int(value, 16))

            elif first_word == 'exit':
                device_manager.remove_all_devices()
                main_loop_running = False

        except Exception as e:
            print('ERROR:',e)
            #raise e


if __name__ == '__main__':
    main()
