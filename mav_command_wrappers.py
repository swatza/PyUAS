
#IMPORTS
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative, Command
import math
from pymavlink import mavutil
import numpy as np


"""
SUMMARY:
Create a loiter command in mavlink global relative frame by providing several arguments based on number of loiters to complete
ARGS:
Number of Loiters [999 = unlimited]
Loiter Radius (Positive = CW; Negative = CCW) [meters]
altitude [meters] with 0 being current altitude
location = [latitude, longitude] with 0 being current lat,lon
"""
def createLoiterCmd(number_of_loiters, loiter_radius, altitude, location):
    # loiter for an unlimited amount of time until next command
    if number_of_loiters == 999:
        newcmd = Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LOITER_UNLIM,0,0, 0, 0, loiter_radius, 0,
                         location[0], location[1], altitude)
    else:
        newcmd = Command(0,0,0,mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LOITER_TURNS,0,0, number_of_loiters, 0, loiter_radius, 0, location[0], location[1], altitude)
    return newcmd


"""
SUMMARY:
Create a loiter command in mavlink global relative frame by providing several arguments based on time to spend loitering
ARGS:
Time to loiter (>= 1200 is unlim) [seconds]
Loiter Radius (Positive = CW; Negative = CCW) [meters]
altitude [meters] with 0 being current altitude
location = [latitude, longitude] with 0 being current lat,lon
"""
def createLoiterTimeCmd(time_to_loiter, loiter_radius, altitude, location):
    if time_to_loiter >= 1200:
        newcmd = Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                         mavutil.mavlink.MAV_CMD_NAV_LOITER_UNLIM,0,0, 0, 0, loiter_radius, 0,
                         location[0], location[1], altitude)
    else:
        newcmd = Command(0,0,0,mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_LOITER_TIME,0,0,time_to_loiter,0,loiter_radius,0,location[0], location[1], altitude)
    return newcmd