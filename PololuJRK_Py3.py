# coding: utf-8
# Updated Version of PololuJRK library
# This version runs on python3 and checks if the desired position
# lies in a defined range
#
# Fabian Müller, 18.07.2017



import serial
from time import sleep
import sys


class PololuJRK:

  __cmd_Init        =       0xAA;
  __cmd_MoveTo      =       0xC0;
  __cmd_ReadError   =       0xB3;
  __cmd_GetPosition =       0xA7;
  __cmd_Stop        =       0xFF;
  __cmd_dutyCycle   =       0xAD;
  __cmd_GetTarget   =       0xA3;

  __minSteps        =       140;
  __maxSteps        =       3610;

  __errorDict = {
        2  : (2, 'No Power Connected'),
        4  : (4, 'Motor Driver Error'),
        8  : (8, 'Input Invalid'),
        16 : (16, 'Input Disconnected'),
        32 : (32, 'Feedback Disconnected'),
        64 : (64, 'Max. Current Exeeded')
    };

  __Is_Ready        =       False;
  __serial          =       0;
  rate              =       9600;
  __port            =       '';
  accuracy          =       4;

  def __init__(self, port):
    self.__port = port;

  def SetPort(self, port):
      self.__port = port;

  def Connect(self):
    if not self.__Is_Ready:
      try:
        self.__serial = serial.Serial(self.__port, baudrate=self.rate, timeout=0.5, interCharTimeout=0.005);

        #init connection sending 0xAA
        self.__serial.write(serial.to_bytes([self.__cmd_Init]));

        self.__Is_Ready = True;

      except Exception as e:
        self.__Is_Ready = False;
        raise Exception('Failed to Init PololuJRK on {} ({})'.format(self.__port, e) );

    return True;

  def __sendCommand(self, cmd, argument = []):
    if self.__Is_Ready:
      try:
        #send command byte
        self.__serial.write(serial.to_bytes([cmd]));

        # if arguments, attach them
        for byte in argument:
          self.__serial.write(serial.to_bytes([byte]));

      except Exception as e:
        self.__Is_Ready = False;
        raise Exception( 'PololuJRK: Error sending command: {} to {} ({})'.format(hex(cmd), e) );

    return True;


  def __readAns(self, nBytes):
    # read nBytes from serial port
    if self.__Is_Ready:
      try:
        ans = self.__serial.read(nBytes);
        return ans;
      except Exception as e:
        self.__Is_Ready = False;
        raise Exception( 'PololuJRK: error reading from {} ({})'.format(self.__port, e) );

  def MotorStop(self):
    if self.__Is_Ready:
      return self.__sendCommand(self.__cmd_Stop);

  def MoveTo(self, pos):
    if self.__Is_Ready and pos >= self.__minSteps and pos <=  self.__maxSteps:

      # the lower 5 bits are attached to the command byte
      cmd = self.__cmd_MoveTo + (pos & 0x1F);
      # the upper 7 bits are sent as the argument
      arg = [(pos >> 5) & 0x7F];

      ans = self.__sendCommand(cmd, arg);

      while True:
        sleep(1);
        currentPos = self.GetPosition();

        if abs(pos - currentPos) <= self.accuracy:
         break;


      return self.MotorStop();

  def GetPosition(self):
    if self.__Is_Ready:
      #request position
      self.__sendCommand(self.__cmd_GetPosition);

      #read answer
      ans = self.__readAns(2);

      # convert answer
      return (ans[0] & 0xff) +  ((ans[1] & 0xff) << 8);

  def GetTarget(self):
    if self.__Is_Ready:
      #request position
      self.__sendCommand(self.__cmd_GetTarget);

      #read answer
      ans = self.__readAns(2);

      # convert answer
      #return(ans);
      return (ans[0] & 0xff) +  ((ans[1] & 0xff) << 8);

  def GoHome(self):
    return self.MoveTo(self.__minSteps);

  def IsReady(self):
    return self.__Is_Ready;

  def Status(self):
    if self.__Is_Ready:
      #request status
      self.__sendCommand(self.__cmd_ReadError);

      # read answer
      ans = self.__readAns(2);
      statusMsg = (ans[0] & 0xff) +  ((ans[1] & 0xff) << 8);

      if (statusMsg < 2):
        return (0, 'Ready');
      else:
        self.__Is_Ready = False;
        if statusMsg in self.__errorDict.keys():
            return self.__errorDict[statusMsg];
        else:
            return (128, 'Serial Comunication Error');


  def Close(self):
      self.__Is_Ready = False;
      self.__serial.Close();


if __name__ == '__main__':

  JRK = PololuJRK('/dev/ttyACM0');
  JRK.Connect();
  print( JRK.Status() );
  JRK.GoHome();
  print( 'zero: ', JRK.GetPosition());

  while True:
    pos = input('move to: ');
    pos = int(pos);
    JRK.MoveTo(pos);
    print( JRK.GetPosition());
    print( JRK.Status() );
