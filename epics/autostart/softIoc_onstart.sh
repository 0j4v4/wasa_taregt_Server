#!/bin/bash -

# start epics softioc
procServ 2000 /home/pi/Apps/epics/base-3.15.6/bin/linux-arm/softIoc -d /home/pi/WASA_Target_Server/epics/WASA_TARGET.db

echo "softIoc started";
