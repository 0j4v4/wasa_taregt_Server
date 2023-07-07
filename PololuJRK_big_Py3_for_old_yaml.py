import serial
import subprocess
import yaml
import time

delay = 0.006


class motor_driver:
    def __init__(self, serial_number):
        self.serialnumber = serial_number
        self.possition_to_set = 0
        self.accuracy = 5       #0.00682*5 = 0.034 mm
    def jrk2cmd(self, *args):
        return subprocess.check_output(['jrk2cmd'] + list(args))
    def Status(self):
        status = yaml.load(self.jrk2cmd('-d', self.serialnumber, '-s', '--full'))
        return status["Overall status"]
    def get_fullStatus(self):
        return (self.jrk2cmd('-d', self.serialnumber, '-s', '--full'))
    def GetPosition(self):
        while True:
            time.sleep(1);
            currentPos = yaml.load(self.jrk2cmd('-d', self.serialnumber, '-s', '--full'))["Scaled feedback"]
            if abs(self.possition_to_set - currentPos) <= self.accuracy:
                break;
        return currentPos

        # while yaml.load(self.jrk2cmd('-d', self.serialnumber, '-s', '--full'))["Error"] not in range(-5,5):
        #     self.set_target(self.possition_to_set)
        # time.sleep(0.1)
        #return yaml.load(self.jrk2cmd('-d', self.serialnumber, '-s', '--full'))["Scaled feedback"]
    def get_serialNumber(self):
        status = yaml.load(self.jrk2cmd('-d', self.serialnumber, '-s', '--full'))
        return status["Serial number"]
    def get_name(self):
        status = yaml.load(self.jrk2cmd('-d', self.serialnumber, '-s', '--full'))
        return status["Name"]
    def get_current(self):
        status = yaml.load(self.jrk2cmd('-d', self.serialnumber, '-s', '--full'))
        return status["Current"]
    def get_error(self):
        status = yaml.load(self.jrk2cmd('-d', self.serialnumber, '-s', '--full'))
        return status["Error"]
    def MoveTo(self, target):
        self.possition_to_set = target
        self.jrk2cmd('-d', self.serialnumber, '--target', str(target))

#
# if __name__ == '__main__':
#     x_motor = motor_driver(x_serial)
#
#     while True:
#         print("motor current possition -> ", x_motor.get_status())
#         pos = input('move to: ');
#         pos = int(pos);
#         x_motor.set_target(pos)
#         dt = abs(pos-int(x_motor.get_position()))
#         #time.sleep(delay*dt)
#         print("motor possition -> " + str(x_motor.get_position()) + " +/- " + str(x_motor.get_error()))
