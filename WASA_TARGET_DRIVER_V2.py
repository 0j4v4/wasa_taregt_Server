#!/usr/bin/python3

#
# 03.2019 o.javakhishvili@fz-juelich.de
#

from PololuJRK_big_Py3 import motor_driver
import sys
import epics
import epics_methods
import time

class motor_controll:
    def __init__(self, motorcount):
        self.y_serial = "00224055"
        self.callibration_y = 0.06821
        self.JRK_Y = motor_driver(self.y_serial);
        print(self.JRK_Y.Status() );

    def SetPosY(self, posY):
        val = float(posY) / self.callibration_y
        self.JRK_Y.MoveTo(round(val))

    def GetPosY(self):
        pos = self.JRK_Y.GetPosition()
        return int(pos) * self.callibration_y

    def GetStatusY(self):
        status = self.JRK_Y.GetPosition()
        return status

if __name__ == "__main__":
    motor = motor_controll(1)
    proc = epics_methods.epics_functions(motor)
    while True:
        epics.poll(evt=1.e-5, iot=0.1)
