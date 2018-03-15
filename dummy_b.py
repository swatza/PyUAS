#IMPORTS
import threading
import Queue
import time
import socket
import select
import sys

sys.path.insert(0, './protobuf')
import PyPackets_pb2

import PyPacket

RECV_BUFF = 8192

def buildNodePacket(data):
	pkt_id = PyPacket.PacketID(PyPacket.PacketPlatform.DUMMY,11)
	pkt = PyPacket.PyPacket()
	pkt.setDataType(PyPacket.PacketDataType.PKT_NODE_HEARTBEAT)
	pkt.setID(pkt_id.getBytes())
	pkt.setData(data) #normally insert a data building part
	return pkt.getPacket() #return the byte array msg
	
def buildGenPacket(data):
	pkt_id = PyPacket.PacketID(PyPacket.PacketPlatform.DUMMY,11)
	pkt = PyPacket.PyPacket()
	pkt.setDataType(PyPacket.PacketDataType.PKT_DMY_MSG)
	pkt.setID(pkt_id.getBytes())
	pkt.setData(data) #normally insert a data building part
	return pkt.getPacket() #return the byte array msg

#SUBSCRIBER
class ReadingThread(threading.Thread):
	def __init__(self, socket):
		threading.Thread.__init__(self)
		self.socket = socket
		self.Quit = False
		
	def run(self):
		inputs = [self.socket]
		outputs = []
		while not self.Quit:
			#check to see if the socket has something
			readable,writable,errorable = select.select(inputs,outputs,inputs,0.01)
			for s in readable:
				#read the something
				bytes, address = s.recvfrom(RECV_BUFF)
				#parse the data 
				print >>sys.stderr, 'recieved "%s" from %s' %(len(bytes), address)
		#-----------------
		#End of While Loop
		self.socket.close()
			
	def setQuit(self):
		self.Quit = True

#PUBLISHER			
class WritingThread(threading.Thread):
	def __init__(self, socket):
		threading.Thread.__init__(self)
		self.socket = socket
		self.Quit = False
		
	def run(self):
		node_freq = 5
		deltaT_node = 999
		#Run loop
		while not self.Quit:
			#check to send node info at 1/10 Hz
			if deltaT_node >= node_freq:
				#create node message 
				m = buildNodePacket('Test from Dummy A')
				#add to queue
				msg_que.put(m)
				#update timer
				tlast_node = time.time()
				
			#check to see if we have any messages in Que to send
			try:
				next_msg = msg_que.get_nowait()
			except Queue.Empty:
				#print 'Output queue is empty'
				empty_que = 1;
			else:
				self.socket.sendto(next_msg,('localhost',NM_PORT))
				print 'sent message at %s' %(time.time())
				
			#Update deltaTs
			deltaT_node = time.time() - tlast_node
			#time.sleep(0.1)
		#-----------------
		#End of While Loop
		self.socket.close()
		
	def buildNodeInfo(self):
		pass
		
	def setQuit(self):
		self.Quit = True
		
PORT = 11000
NM_PORT = 16000
IP = 'localhost'
#Create Out Socket
s_out = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#Create In Socket
s_in = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s_in.bind(('',PORT))

#Create message out que system
msg_que = Queue.Queue()

#Start threads for I/O
rthread = ReadingThread(s_in)
rthread.start()
wthread = WritingThread(s_out)
wthread.start()

#RUNTIME
for c in range(10):
	#add a message to queue
	msg_que.put(buildGenPacket('This is a Dummy Msg'))
	#count up after sleeping
	time.sleep(1)
	c += 1

wthread.setQuit()
rthread.setQuit()