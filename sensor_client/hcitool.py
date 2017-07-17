
import pexpect

from config import *

class HCITOOL():
    def __init__(self):
        self.htool = pexpect.spawnu('sudo hcitool lescan', timeout = 3)

        self.list_of_lines = []

    def __del__(self):
        # When object is deleted, make sure to ctrl + C out of hcitool
        self.htool.sendline('\003')

    def add_into_list(self, string_to_compare):
        length_of_mac_address = len('AC:37:43:B1:79:5B')
        mac_address = string_to_compare[:length_of_mac_address]
        for line in self.list_of_lines:
            if mac_address in line:
                if string_to_compare.find('(unknown)') == -1 and line.find('(unknown)') != -1:
                    self.list_of_lines.remove(line)
                    self.list_of_lines.append(string_to_compare)
                    return
                else:
                    return

        self.list_of_lines.append(string_to_compare)

    def read_output(self):

        try:
            for line in self.htool:
                line = line.replace('\r', '')
                line = line.replace('\n', '')
                self.add_into_list(line)
        except pexpect.exceptions.EOF:
            pass
        finally:
            return self.list_of_lines



if __name__ == '__main__':
    tool = HCITOOL()
    output = tool.read_output()
    print(output)
