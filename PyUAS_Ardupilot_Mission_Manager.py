#IMPORTS
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative, Command
import math
from pymavlink import mavutil
import numpy as np
import logging
import mav_command_wrappers

import time

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
        self.testCommands() #??? do we really need?

        #set a mission list
        self.missionlist = []


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

    def setCommandList(self, list):
        #creates a command list object with commands in list
        cmds = self.commands
        cmds.clear()
        for cmd in list:
            cmds.add(cmd)
        return cmds #not really needed since its a class member

    def vehicleState(self):
        self.logger.info("Global Location (relative altitude): %s", self.vehicle.location.global_relative_frame)
        self.logger.info("Attitude: %s", self.vehicle.attitude)
        self.logger.info("Velocity: %s", self.vehicle.velocity)
        self.logger.info("Groundspeed: %s", self.vehicle.groundspeed)
        self.logger.info("Last Heartbeat: %s", self.vehicle.last_heartbeat)

    def uploadTakeOff(self):
        print "Creating and Uploading Takeoff Cmd"
        missionlist = []
        cmd_TO = Command(0,0,0,mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, self.altitude)
        cmd_RTL = Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, self.altitude)
        missionlist.append(cmd_TO)
        missionlist.append(cmd_RTL)
        self.setCommandList(missionlist)
        self.uploadCommands()

    def uploadReturnToHome(self):
        print "Creating and Uploading RTL Cmd"
        missionlist = []
        cmd_RTL = Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                          mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, self.altitude)
        missionlist.append(cmd_RTL)
        self.setCommandList(missionlist)
        self.uploadCommands()

    def resetMission(self):
        self.missionlist = [] #does this work?

    def addToMission(self, cmd):
        print "Cmd added to mission list"
        self.missionlist.append(cmd)

    def getCmdinMission(self, index):
        if index > len(self.missionlist):
            return None
        else:
            return self.missionlist[index]

    def setCmdinMission(self, index, cmd):
        #Return true or false to indicate success
        if index > len(self.missionlist):
            print "Index can't be reached; appending to end"
            self.addToMission(cmd)
            return False
        else:
            self.missionlist[index] = cmd
            return True

    def activateMission(self):
        self.setCommandList(self.missionlist)

    def getCommands(self):
        self.commands.download()
        self.commands.wait_ready() #wait until download is complete

    def getNextWaypoint(self):
        return vehicle.commands.next

    def uploadCommands(self):
        self.commands.upload()

    def goToAuto(self):
        self.vehicle.mode = VehicleMode("AUTO")

    def goToGuided(self):
        self.vehicle.mode = VehicleMode("GUIDED")

    def goToRTL(self):
        self.vehicle.mode = VehicleMode("RTL") #or is it ReturnToLaunch

    #Number of times if set to -1 is indefinite repeat until it moves to next command in the list
    def JumpTo(self, waypoint_ind, number_of_times):
        return Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_DO_JUMP, 0, 0, waypoint_ind,
                number_of_times, 0, 0, 0, 0, 0)



if __name__== "__main__":
    # what does this lambda function do
    clear = lambda: os.system('clear')

    # Parameters
    connection_string = "udp:127.0.0.1:14552" #Update this for actual aircraft test flight
    home = 40.038977,-105.232176 #UPdate Me
    time_between_uploads = 30
    number_of_loiters = 3
    loiter_radius = 50
    alt = 100 #this feet or meters?
    location1 = 40.007355,-105.262496 #Update Me
    location2 = 40.130672,-105.244495 #Update Me
    my_wpt_counter = 0

    print "Creating APMM"
    #Initialize the PyUAS Ardupilot mission manager
    apmm = ArduPilotMissionManager(connection_string, "aircraft_test", alt, home)

    #Upload Takeoff and loiter at home command
    #print "TakeOff Sequence"
    #apmm.uploadTakeOff() #add take off and RTL
    #apmm.goToAuto()
    #time.sleep(time_between_uploads) #sleep 20 s

    #upload first command of loiter X
    print "First Command Sequence: Head to Location 1"
    new_cmd = mav_command_wrappers.createLoiterCmd(number_of_loiters,loiter_radius,alt,location1) #create loiter command
    apmm.resetMission() #reset the mission list here
    apmm.addToMission(new_cmd)  #add it to the mission list
    apmm.activateMission() #move the mission list into the command list buffer
    apmm.uploadCommands() # upload that command list buffer to the ardupilot
    apmm.goToAuto() #I can do this or he can...

    #Wait N seconds
    time.sleep(time_between_uploads) #sleep 20 s

    #upload second command of loiter Y
    print "Second Command Sequence: Head to Location 2 -> timer"
    new_cmd = mav_command_wrappers.createLoiterTimeCmd(300, loiter_radius, alt,
                                                   location2)  # create loiter command
    apmm.goToGuided() #Pause mission by going to guided
    apmm.resetMission()
    apmm.addToMission(new_cmd)  # add it to the mission list
    apmm.activateMission()  # move the mission list into the command list buffer
    apmm.uploadCommands()  # upload that command list buffer to the ardupilot
    apmm.goToAuto() #restart the mission (goes to mission 1)

    #wait N seconds
    time.sleep(time_between_uploads)  # sleep 20 s

    #uplaod first command of loiter X
    print "Third Command Sequence: Head to Location 1"
    new_cmd = mav_command_wrappers.createLoiterCmd(number_of_loiters, loiter_radius, alt,
                                                   location1)  # create loiter command
    apmm.goToGuided()  # Pause mission by going to guided
    apmm.resetMission()
    apmm.addToMission(new_cmd)  # add it to the mission list
    apmm.activateMission()  # move the mission list into the command list buffer
    apmm.uploadCommands()  # upload that command list buffer to the ardupilot
    apmm.goToAuto()

    #wait N seconds
    time.sleep(time_between_uploads)  # sleep 20 s

    #return to home
    print "Fourth Command Sequence: Return To Launch"
    apmm.goToRTL()