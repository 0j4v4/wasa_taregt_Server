#!/usr/bin/python3

#
# 03.2019 o.javakhishvili@fz-juelich.de
#

from PololuJRK_Py3 import PololuJRK
import sys
import epics
import epics_methods
import time
import signal
import logging

import serial.tools.list_ports as list_ports


class logger:
    def __init__(self):
        self.gLogger = logging.getLogger('WASA_Target_Server');
        self.gLogger.setLevel(logging.INFO);

        # create a file handler
        gLogFileHandle = logging.FileHandler('log/main.log')
        gLogFileHandle.setLevel(logging.INFO);

        # create a logging format
        gLogFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        gLogFileHandle.setFormatter(gLogFormatter)

        # add the handlers to the logger
        self.gLogger.addHandler(gLogFileHandle)

    def add_log(self,level,data):
        if level == "error":
            self.gLogger.error(data)
        elif level == "info":
            self.gLogger.info(data)

class motor_controll:
    def __init__(self, motorcount,log):
        self.logger = log
        self.identifier = '1FFB:0083'
        self.min_pos = 0
        self.max_pos = 152.5
        self.min_step = 150
        self.max_step = 3500
        #self.callibration_y = 0.06821
        usb = self.findUSBPort(self.identifier)

        if usb == None:
            self.logger.add_log("error",'No USB port found for the identifier {}'.format(self.identifier));
            #print('No USB port found for the identifier {}'.format(self.identifier));
        else:
            self.logger.add_log("info",'Found USB port for the identifier {} on {}'.format(self.identifier, usb));
            #print('Found USB port for the identifier {} on {}'.format(self.identifier, usb));
            #self.JRK_Y = PololuJRK('/dev/ttyACM0');
            self.JRK_Y = PololuJRK(usb);
        #print(self.JRK_Y)
        if self.JRK_Y.Connect():
            var = self.JRK_Y.Status()
            self.logger.add_log("info",'JRK = {}'.format(var));
            #print( self.JRK_Y.Status());

    def findUSBPort(self,identifier):
        ''' searches the connected usb ports for a given identifier (vendorID:productID)
            and returns the associated port if any else it will return NONE.
            If multiple port are found for the same identifier, the port with the lower
            number gets chosen '''

        portlist = list();

        for port in list_ports.comports():
            try:
                current_identifier = port[2].split(' ')[1].split('=')[1];
                # print(port[0]+"  ooo  "+port[1]+'  ooo  '+port[2])
                # current_identifier = port[2].split('=')[1].split(' ')[0];
                if current_identifier == self.identifier:
                    portlist.append(port[0]);
                    #print( portlist );
            except Exception as e:
                # this port does not have a vid:pid usb identifier.. skip it
                #print('Error while searching for USB port: {}'.format(e));
                continue;

        if len(portlist):
            # sort the list
            portlist.sort(reverse=False);
            return portlist[0]; # will return the port with the lowest port number

        else:
            # no ports found that maches the identifier
            return None;

    def mm_to_steps(self,mm):
        steps = int( float(mm) *((self.min_step - self.max_step) / self.max_pos) + self.max_step)
        return steps
    def steps_to_mm(self,steps):
        mm = round(10 * ( (steps - self.max_step)*(self.max_pos / (self.min_step - self.max_step)))) / 10.0
        return mm
    def SetPosY(self, posY):
        val = self.mm_to_steps(posY)
        self.JRK_Y.MoveTo(val)

    def GetPosY(self):
        pos = self.JRK_Y.GetPosition()
        return self.steps_to_mm(pos)

    def GetStatusY(self):
        status = self.JRK_Y.GetPosition()
        return status


if __name__ == "__main__":
    log = logger()
    motor = motor_controll(1,log)
    proc = epics_methods.epics_functions(motor,log)
    signal.signal(signal.SIGINT, proc.oninterupt)
    signal.signal(signal.SIGTERM, proc.onterminate)
    log.add_log("info","server has started")
    while True:
        epics.poll(evt=1.e-5, iot=0.1)
