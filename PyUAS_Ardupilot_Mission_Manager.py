#IMPORTS
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative, Command
import math
from pymavlink import mavutil
import numpy as np
import logging

class ArduPilotMissionManager(object):
    #Initialize the object by creating the connection
    def __init__(self, connection, name, altitude, home, log_mode=10):
        # CREATE A LOGGER
        self.logger = logging.getLogger("ArduPilot_Mission_Manager:" + name)
        self.logger.setLevel(log_mode)
        my_handler = logging.StreamHandler()
        self.logger.addHandler(my_handler)
        self.logger.info("Connecting to vehicle on: %s",connection)

        #connect to the vehicle
        self.vehicle = connect(connection,wait_ready=True)

        #check to see if connection was established?

        #set home and altitude
        self.home = home
        self.altitude = altitude #TODO! add something to check for relative vs absolute

        #Get the command list from the vehicle and test
        self.commands = self.vehicle.commands
        self.testCommands()

    def testCommands(self):
        newcmd = Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, self.home[0], self.home[1], self.altitude)
        self.commands.add(newcmd)
        self.commands.clear()

    def setHomeLocation(self, home_location):
        self.home = home_location

    #TODO! Finish this function
    def printCommandList(self):
        #Prints a command list object to the terminal
        self.logger.info("Mission in %s's Command List:",self.name)
        next_pt = self.vehicle.commands.next
        #print the command list
        for cmd in self.commands:
            lat=cmd.x
            lon=cmd.y
            alt=cmd.z
        #END

    def vehicleState(self):
        self.logger.info("Global Location (relative altitude): %s", self.vehicle.location.global_relative_frame)
        self.logger.info("Attitude: %s", self.vehicle.attitude)
        self.logger.info("Velocity: %s", self.vehicle.velocity)
        self.logger.info("Groundspeed: %s", self.vehicle.groundspeed)
        self.logger.info("Last Heartbeat: %s", self.vehicle.last_heartbeat)
