#!/bin/bash -

# go to directory
cd /home/pi/WASA_Target_Server/

# start wasa server
python3 WASA_TARGET_DRIVER_V1.py &


echo "WASA Target Server has started";
