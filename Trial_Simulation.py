'''
Baseline Simulation using 1A Kinematics AutoPilot Model
'''

import sys
import threading
import time
import socket
import Queue
import select
#PyUAS items
import AutoPilotModels
import PyPacket

RECV_BUFF = PyPacket.RECVBUFF
NM_PORT = 16000
shutdown_event = threading.Event()


class WritingThread(threading.Thread):
	def __init__(self,socket):
		threading.Thread.__init__(self)
		self.socket = socket
		
	def run(self):
		while not shutdown_event.is_set():
			try:
				next_msg = theirQue.get_nowait()
			except Queue.Empty:
				pass
			else:
				self.socket.sendto(next_msg,('localhost',NM_PORT))
				print 'sent state message at %s' %(time.time())
		#End while loop
		self.socket.close()
		print 'Closing Writing Thread'

#Create the que for the autopilot thingy
theirQue = Queue.Queue()

#Create the sockets for communication to the network manager
socket_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#socket_out.setblocking(0)
socket_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#socket_in.setblocking(0)
#socket_in.bind(('',19000)) #bind to the port we want 

#Need to create a subscriber if you want to listen to anything like new waypoints


#Create the autopilot task and start it
AutoPilotTask = AutoPilotModels.Simple1AKinematicsAutoPilotModel(theirQue, shutdown_event)
AutoPilotTask.start()
wThread = WritingThread(socket_out)
wThread.start()


while threading.active_count() > 1:
	try:
		time.sleep(.5)
		#for errors 
	except (KeyboardInterrupt, SystemExit):
		shutdown_event.set()
		socket_out.close()
		socket_in.close()
		print('Ending AutoPilot Simulation')
print 'Ending System'
sys.exit()
			