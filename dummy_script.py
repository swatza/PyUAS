'''
Dummy Test Script for acting as a Node/Process for Network Manager and PyPacket testing. 

Future Work needs to investigate ways of broadening the subscribers of a process to something
more than being hard coded. Ways to check for all of a certain message type or something

Copyright: Spencer Watza
'''


#IMPORTS
import threading
import Queue
import time
import socket
import select
import sys

#PyUAS Libs
sys.path.insert(0,'./protobuf')
import PyPackets_pb2
import PyPacket
import Subscriber

RECV_BUFF = 8192 #We should store somewhere in the library for more global usage
#CHANGE THESE IF COPIED TO A NEW NAME
MYNUM=10
MYSTRING="I am Dummy 10"
PORT = MYNUM * 1000

shutdown_event = threading.Event()

#----------------------------------------
# Function to build NodeHeartBeat Packet
#----------------------------------------
def buildNodeHeartBeatPacket(subscribers, PacketNodeCounter):
	#Create the ID information for the packet
	pkt_id = PyPacket.PacketID(PyPacket.PacketPlatform.DUMMY,MYNUM)
	pkt = PyPacket.PyPacket()
	pkt.setDataType(PyPacket.PacketDataType.PKT_NODE_HEARTBEAT)
	pkt.setID(pkt_id.getBytes())
	#Define the basic components
	msg = PyPackets_pb2.NodeHeartBeat()
	msg.packetNum = PacketNodeCounter
	msg.ID = str(pkt.getID())
	msg.time = time.time()
	#add all the subscriber information
	c = 0;
	for n in subscribers:
		new = msg.sub.add()
		new.id = str(n.ID)
		new.datatype = str(n.TYPE)
		new.port = n.PORT
		new.address = n.IP
		new.msgfreq = n.FREQ
		c += 1 #increment counter
	#end loop
	#serialize the data into packet
	data_str = msg.SerializeToString()
	pkt.setData(data_str)
	#pkt.displayPacket()
	del msg
	return pkt.getPacket() #return the byte array msg

#----------------------------------------
# Function to build a Dummy Packet
#----------------------------------------
def buildDummyPacket(PacketDummyCounter):
	#Create the id information for the packet
	pkt_id = PyPacket.PacketID(PyPacket.PacketPlatform.DUMMY,MYNUM)
	pkt = PyPacket.PyPacket()
	pkt.setDataType(PyPacket.PacketDataType.PKT_DMY_MSG)
	pkt.setID(pkt_id.getBytes())
	#Define the basic components
	msg = PyPackets_pb2.dummy_msg()
	msg.packetNum = PacketDummyCounter
	msg.ID = str(pkt.getID())
	msg.time = time.time()
	#Add the data
	msg.s = MYSTRING
	#Serialize the data
	data_str = msg.SerializeToString()
	pkt.setData(data_str)
	#pkt.displayPacket()
	del msg
	return pkt.getPacket()
	
#----------------------------------------
# Class for the Reading Thread
#----------------------------------------
class ReadingThread(threading.Thread):
	def __init__(self,socket):
		threading.Thread.__init__(self)
		self.socket = socket
		self.Quit = False
		
	def run(self):
		inputs = [self.socket]
		outputs = []
		while not shutdown_event.is_set():
			#check to see if the sockets have soemthing
			readable, writable, errorable = select.select(inputs, outputs, inputs, 0.01)
			for s in readable:
				#read 
				bytes, address = s.recvfrom(RECV_BUFF)
				#parse the data
				print >>sys.stderr, 'recieved "%s" from %s'%(len(bytes),address)
		#---------
		#End of while Loop
		self.socket.close()
		
	def setQuit(self):
		self.Quit = True
		
#----------------------------------------
# Class for the Writing Thread
#----------------------------------------
class WritingThread(threading.Thread):
	def __init__(self, socket):
		threading.Thread.__init__(self)
		self.socket = socket
		self.Quit = False
		
	def run(self):
		node_rate = 5
		deltaT_node = 999
		PacketCounterNode = 1;
		TestSubs = []
		#Generate the subs here (hardcoded) 
		subA = Subscriber.Subscriber(PyPacket.PacketDataType.PKT_DMY_MSG,PyPacket.PacketID(PyPacket.PacketPlatform.DUMMY,20).getBytes(),PORT,'localhost',1)
		subB = Subscriber.Subscriber(PyPacket.PacketDataType.PKT_DMY_MSG,PyPacket.PacketID(PyPacket.PacketPlatform.DUMMY,20).getBytes(),PORT,'localhost',1)
		subC = Subscriber.Subscriber(PyPacket.PacketDataType.PKT_DMY_MSG,PyPacket.PacketID(PyPacket.PacketPlatform.DUMMY,30).getBytes(),PORT,'localhost',1)
		subD = Subscriber.Subscriber(PyPacket.PacketDataType.PKT_DMY_MSG,PyPacket.PacketID(PyPacket.PacketPlatform.DUMMY,40).getBytes(),PORT,'localhost',1)
		TestSubs.append(subA)
		TestSubs.append(subB)
		TestSubs.append(subC)
		TestSubs.append(subD)
		#Run loops
		while not shutdown_event.is_set():
			#check to send node info at desired frequency
			if deltaT_node >= node_rate:
				#create node message
				m = buildNodeHeartBeatPacket(TestSubs,PacketCounterNode)
				#add to queue
				msg_que.put(m)
				PacketCounterNode += 1
				#update timer
				tlast_node = time.time()
				
			#Check to see if we have any messages in Que to send
			try:
				next_msg = msg_que.get_nowait()
			except Queue.Empty:
				empty_que = 1;
			else:
				self.socket.sendto(next_msg,('localhost',NM_PORT))
				print 'sent message at %s' %(time.time())
				
			#update deltaTs
			deltaT_node = time.time() - tlast_node
			#time.sleep(0.1)
		#-------------
		#End of While Loop
		self.socket.close()
		
	def setQuit():
		self.Quit = True
		
#----------------------------------------
# Main Run Time Area
#----------------------------------------	
NM_PORT = 16000
PacketDummyCounter = 1
dummy_msg_rate = 1;
IP = 'localhost'
#Create out socket
s_out = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#Create in Socket
s_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_in.bind(('',PORT))

#Create message out que system
msg_que = Queue.Queue()

#Start Threads for I/O
wthread = WritingThread(s_out)
wthread.start()
rthread = ReadingThread(s_in)
rthread.start()

#Runtime 
deltaT_dummy = 999
tlast_dummy = 0; #so it sends a message as soon as it starts
while threading.active_count() > 1:
    try:
        if deltaT_dummy >= dummy_msg_rate:
            #make a dummy packet message
            msg_que.put(buildDummyPacket(PacketDummyCounter))
            PacketDummyCounter += 1
            tlast_dummy = time.time()
        #update the deltaT 
        deltaT_dummy = time.time() - tlast_dummy
    except (KeyboardInterrupt, SystemExit):
        shutdown_event.set()
        print "Closing Process"
        print 'This many dummy messages were sent: %i' %(PacketDummyCounter)
#End while
sys.exit()