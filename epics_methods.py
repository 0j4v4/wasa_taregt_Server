from epics import PV, caget, caput
#from WASA_TARGET_DRIVER_V2 import motor_controll
import time

pv_names = {
"SETPOS_Y":"EXP:JEDI:WASA:InBeamPos:Y",
"GETPOS_Y":"EXP:JEDI:WASA:GetPos:Y",
"DELTAPOS_Y":"EXP:JEDI:WASA:DeltaPos:Y",
"HOME_Y":"EXP:JEDI:WASA:HOME:Y",
"STATUS_Y":"EXP:JEDI:WASA:Status:Y",
"MODE":"EXP:JEDI:WASA:MODE",
"GUI":"EXP:JEDI:WASA:GUI",
"COMMAND":"EXP:JEDI:WASA:COMMAND",
"CYCLE":"EXP:JEDI:WASA:CYCLE",
"INSTANCE": "EXP:JEDI:WASA:INSTANCE"
}

gui_mode = "OFF"
operating_mode = "MANUAL"
instance_count = 0

class epics_functions:
    def __init__(self,motor,log):
        self.logger = log
        self.motor = motor
        self.epics_variables = dict()
        self.makePVdict()


    def makePVdict(self):

        '''for each pv name in pv_names dictionary creates epics PV object and writes it to epics variables dictionary'''
        pv_list = list()
        keys = list(pv_names.keys())
        values = pv_names.values()
        for n in values:
            pv_list.append(PV(str(n)))
        self.epics_variables.update(dict(zip(keys,pv_list)))
        time.sleep(0.1)
        #print(self.epics_variables)
        self.epics_variables["MODE"].add_callback(self.MODE_CHANGED)
        # self.epics_variables["SETPOS_X"].add_callback(self.SETPOS_X_CHANGED)
        # self.epics_variables["DELTAPOS_X"].add_callback(self.DELTAPOS_X_CHANGED)
        # self.epics_variables["HOME_X"].add_callback(self.HOME_X_CHANGED)
        self.epics_variables["SETPOS_Y"].add_callback(self.SETPOS_Y_CHANGED)
        self.epics_variables["DELTAPOS_Y"].add_callback(self.DELTAPOS_Y_CHANGED)
        self.epics_variables["HOME_Y"].add_callback(self.HOME_Y_CHANGED)
        self.epics_variables["GUI"].add_callback(self.GUI_CHANGED)
        self.epics_variables["COMMAND"].add_callback(self.COMMAND_CHANGED)
        self.epics_variables["INSTANCE"].add_callback(self.INSTANCE_CHANGED)
        global operating_mode
        operating_mode = self.Read_PV("MODE")
        global gui_mode
        gui_mode = self.Read_PV("GUI")
        global instance_count
        instance_count = self.Read_PV("INSTANCE")
        self.logger.add_log("info","gui instances are {}".format(instance_count))
        #print("gui instances are ",instance_count)
        #self.epics_variables["CYCLE"].add_callback(self.CYCLE_CHANGED)

    def COMMAND_CHANGED(self, pvname, value, timestamp, cb_info, **kwargs):
        #print ("command changed new command -> ",value)
        if value == "MOVE_Y_INBEAM":
            self.logger.add_log("info","move y in beam {}".format(value))
            self.MOVE_INBEAM("Y")
        elif value == "MOVE_Y_OUTBEAM":
            self.logger.add_log("info","move y out beam {} ".format(value))
            self.MOVE_OUTBEAM("Y")
        elif value == "MOVE_Y_HOME":
            self.logger.add_log("info","move y home {} ".format(value))
            self.MOVE_HOME("Y")
        else:
            self.logger.add_log("info","command reset")
            #print("command reset")

    def MOVE_INBEAM(self, axis = "Y"):
        self.motor.SetPosY(self.Read_PV("SETPOS_Y"))
        pos = self.motor.GetPosY()
        status = self.motor.GetStatusY()
        self.Write_PV("STATUS_Y", "Y -> {0}, JRK Status -> {1}".format(round(pos,5),status))
        self.Write_PV("COMMAND", "WAITING")
    def MOVE_OUTBEAM(self, axix = "Y"):
        val = float(self.Read_PV("SETPOS_Y")) - float(self.Read_PV("DELTAPOS_Y"))
        self.motor.SetPosY(val)
        pos = self.motor.GetPosY()
        status = self.motor.GetStatusY()
        self.Write_PV("STATUS_Y", "Y -> {0}, Status -> {1}".format(round(pos,5),status))
        self.Write_PV("COMMAND", "WAITING")
    def MOVE_HOME(self, axis = "Y"):
        self.motor.SetPosY(self.Read_PV("HOME_Y"))
        pos = self.motor.GetPosY()
        status = self.motor.GetStatusY()
        self.Write_PV("STATUS_Y", "Y -> {0}, Status -> {1}".format(round(pos,5),status))
        self.Write_PV("COMMAND", "WAITING")

    def CYCLE_CHANGED(self, pvname, value, timestamp, cb_info, **kwargs):
        if value == 1:
            self.MOVE_INBEAM("Y")
            self.logger.add_log("info","cycle is on")
            #print ("cycle is on")
        elif value == 0:
            self.MOVE_OUTBEAM("Y")
            self.logger.add_log("info","cycle is off")
            #print("cycle is off")
        else:
            self.logger.add_log("error","undefined cycle state")
            #print("error undefined cycle state")
    def INSTANCE_CHANGED(self, pvname, value, timestamp, cb_info, **kwargs):
        global instance_count
        instance_count = value
        if instance_count == 0:
            self.logger.add_log("info","no gui instances detected!!! setting motor position to [HOME]")
            #print("no gui instances detected!!! setting motor position to [HOME]")
            self.MOVE_HOME("Y")
            #self.Write_PV("INSTANCE","0")
        self.logger.add_log("info","instance count changed, new count = {}".format(instance_count))
        #print("instance count changed, new count = ",instance_count)

    def MODE_CHANGED(self, pvname, value, timestamp, cb_info, **kwargs):
        global operating_mode
        operating_mode = value
        if operating_mode == "MANUAL":
            self.Write_PV("COMMAND", "WAITING")
            self.epics_variables["CYCLE"].clear_callbacks()
        elif operating_mode == "AUTO":
            var = self.Read_PV("CYCLE")
            print(var)
            if var == "1.0":
                self.MOVE_INBEAM("Y")
            elif var == "0.0":
                self.MOVE_OUTBEAM("Y")
            self.epics_variables["CYCLE"].add_callback(self.CYCLE_CHANGED)
        self.logger.add_log("info","mode changed {}".format(operating_mode))
        #print("mode changed ", operating_mode)

    def SETPOS_Y_CHANGED(self, pvname, value, timestamp, cb_info, **kwargs):
        if operating_mode == "MANUAL" and gui_mode == "ON":
            self.logger.add_log("info","PV -> {0} has changed to -> {1}, server time -> {2}".format(pvname,value,timestamp))
            #print("PV -> {0} has changed to -> {1}, change time -> {2}".format(pvname,value,timestamp))
    def DELTAPOS_Y_CHANGED(self, pvname, value, timestamp, cb_info, **kwargs):
        if operating_mode == "MANUAL" and gui_mode == "ON":
            # self.Write_PV("STATUS_Y",str("delta y changed -> {0}".format(value)))
            # self.Write_PV("DELTAPOS_Y", value)
            self.logger.add_log("info","PV -> {0} has changed to -> {1}, server time -> {2}".format(pvname,value,timestamp))
            #print("PV -> {0} has changed to -> {1}, change time -> {2}".format(pvname,value,timestamp))
    def HOME_Y_CHANGED(self, pvname, value, timestamp, cb_info, **kwargs):
        if operating_mode == "MANUAL" and gui_mode == "ON":
            # self.Write_PV("STATUS_Y",str("home y changed -> {0}".format(value)))
            # self.Write_PV("HOME_Y", value)
            self.logger.add_log("info","PV -> {0} has changed to -> {1}, server time -> {2}".format(pvname,value,timestamp))
            #print("PV -> {0} has changed to -> {1}, change time -> {2}".format(pvname,value,timestamp))

    def GUI_CHANGED(self, pvname, value, timestamp, cb_info, **kwargs):
        global gui_mode
        gui_mode = value
        # if value == "OFF":
        #     print(type(insdatce_count))
        #     self.MOVE_HOME("Y")
        # else:
        #     print("else- wtf ", type(instance_count))
        self.logger.add_log("info","guistate changed {}".format(gui_mode))
        #print("guistate changed ", gui_mode)

    def Write_PV(self, name, data):
        self.epics_variables[name].value = data
        time.sleep(0.05)
        return self.epics_variables[name].value

    def Read_PV(self, name):
        #print(epics_variables)
        return (str(self.epics_variables[str(name)].value))
    def oninterupt(self, signal, frame):
        self.logger.add_log("info","keyboard interupt {},  {} ".format(signal, frame))
        #print("keyboard interupt ", signal, frame)
        self.motor.SetPosY(0)
        exit(0)
    def onterminate(self, signal, frame):
        self.logger.add_log("info","proccess terminated {},  {} ".format(signal, frame))
        #print("keyboard interupt ", signal, frame)
        self.motor.SetPosY(0)
        exit(0)
