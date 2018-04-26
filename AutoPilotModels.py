
import sys
import time
import threading
import math
#PyUAS Lib
import PyPacket
sys.path.insert(0,'./protobuf') #get the path to the protobuf format
import PyPackets_pb2
import assorted_lib
import GuidanceAlgorithms
import EquationsOfMotion
import Waypoints

#external
from google.protobuf import json_format


'''
A simple autopilot based on 1A Kinematic model for an aircraft
'''
class Simple1AKinematicsAutoPilotModel(threading.Thread):
	
	#State: Pn,Pe,ChiDot,Chi,HeightDot,Height,Va
	def __init__(self, msgQue, shutdownEvent):
		threading.Thread.__init__(self)
		self.runrate = 10#in Hz
		self.GM = GuidanceAlgorithms.Simple_1A_Guidance(True) #Go clockwise
		self.EoM = EquationsOfMotion.OneAKinematicsEoM() #Default options
		self.myQue = msgQue
		self.packetCounter = 0
		self.shutdown_event = shutdownEvent
		
		#Load in the initial state and center LLA
		self.state = [0,0,0,0,0,1700,15] #set the state
		self.centerLLA = [40.145081,-105.237551,1700]
		boulderLLA = [40.130663,-105.244560,1700]
		boulderENU = assorted_lib.LLA2ENU(boulderLLA,self.centerLLA)
		print boulderENU
		self.initial_waypoint = Waypoints.Waypoint(boulderLLA,boulderENU,1700, 0, 100, 100)
		#Need a logger at some point
		
	def run(self):
		#Real time simulation or as close as possible
		thisState = self.state
		lastTime = time.time()
		waypoint = self.initial_waypoint
		while not self.shutdown_event.is_set():
			#run the model at the specified run rate
			dT = time.time() - lastTime
			if (dT >= 1):
				#Do How do we get a new waypoint?
				
				#Do the guidance / control stuff
				Cmds = self.GM.circleLoiterCalc(waypoint,thisState)
				#print Cmds
				#Do the equations of motion stuff
				stateDot = self.EoM.calculateDerivatives(thisState,Cmds)
				#print stateDot
				thisState = self.EoM.integrateState(thisState,stateDot,dT)
				#print thisState
				#Output the states
				self.writeOutStates(thisState,waypoint)
				
				#Calculate new last time
				lastTime = time.time()
				
				#Sleep for a bit
			#End If Loop
			time.sleep(0.02)
		#End while
				
			
	def writeOutStates(self, states, waypoint):
		#create packet
		thisPacket = PyPacket.PyPacket()
		pktid = PyPacket.PacketID(PyPacket.PacketPlatform.AIRCRAFT,10)
		myidbytes = pktid.getBytes()
		thisPacket.setDataType(PyPacket.PacketDataType.PKT_AUTOPILOT_PIXHAWK)
		thisPacket.setID(pktid.getBytes())
		
		#increment counter
		self.packetCounter += 1
	
		msg = PyPackets_pb2.AircraftPixhawkState()
		msg.packetNum = self.packetCounter
		msg.ID = "AC 10"
		msg.time = time.time()
		
		#convert NED to LLA 
		lla = assorted_lib.NED2LLA([states[0],states[1],states[5]],self.centerLLA)
		
		msg.LLA_Pos.x = lla[0]#lat
		msg.LLA_Pos.y = lla[1]#lon
		msg.LLA_Pos.z = -lla[2]#Alt (ASL)
		
		msg.velocity.x = math.cos(states[3])*states[6]
		msg.velocity.y = math.sin(states[3])*states[6]
		msg.velocity.z = states[4]
		
		msg.attitude.x = 0
		msg.attitude.y = 0
		msg.attitude.z = states[3] #send in radians
		
		msg.airspeed = states[6]
		
		#optional
		msg.omega.x = 0
		msg.omega.y = 0
		msg.omega.z = states[2]
		
		msg.mode = "1A Model Sim"
		
		#optional
		msg.distance_to_mav = 0
		
		#optional
		msg.batteryStatus.voltage = 12.0
		msg.batteryStatus.current = 0.0
		
		#optional 
		msg.currentWaypoint.LLA_Pos.x = waypoint.lat#lat
		msg.currentWaypoint.LLA_Pos.y = waypoint.lon#lon
		msg.currentWaypoint.LLA_Pos.z = waypoint.asl#ASL
		msg.currentWaypoint.cost = 0
		
		#Serialize Msg
		datastr = msg.SerializeToString()
		thisPacket.setData(datastr)
		
		#Add to Que
		self.myQue.put(thisPacket.getPacket())
		print 'Added another message to the que; number %i' %(self.packetCounter)