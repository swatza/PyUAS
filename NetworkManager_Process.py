'''
Author: Spencer Watza

Network Manager Independent Process

Summary: This program will run on a machine to manage routing and other information. 

Design 1: All communication routes through this process with outgoing/incoming messages being forwarded
Design 2: This process just maintains the information about who is routing to who so systems don't need to know 
everyone's details in maps of publish-subscribe format


Notes: All Network Managers are listening and sending out on Port 16000 to each other with UDP protocol

'''

import socket
import sys
import select
import time
import Queue

sys.path.insert(0, './protobuf')
import PyPackets_pb2

import PyPacket
import Subscriber

#============
# Functions
#============

def parsePacket(pkt,SubList):
	#print the packet
	#pkt.displayPacket()
	#get the data type
	data_type = pkt.getDataType()
	#get the identifier
	identifier = pkt.getID()
	#check for subscribers internal and external
	sendList = []
	for s in SubList:
		if s.TYPE == data_type:
			if s.ID == identifier:
				sendList.append(s)
	#Return send list
	return sendList
	
def forwardPacket(pkt, out_socket_queues,SubList):
	sList = parsePacket(pkt,SubList) #figured out who to send the packet to
	#for every address in the list, add it to the correct queue
	for c in sList:
		out_socket_queues.put([c.getAddress(),pkt.getPacket()])
	return out_socket_queues
	
def updateSubListFromNode(pkt,SubList):
	#get the data string from the packet
	data_str = str(pkt.getData())
	#parse into type using protobuf
	gb_msg = PyPackets_pb2.NodeHeartBeat()
	gb_msg.ParseFromString(data_str)
	#loop through subs in heartbeat
	for c in len(gb_msg.sub):
		ID = bytearray(gb_msg.sub[c].id)
		DT = bytearray(gb_msg.sub[c].datatype)
		intPT = gb_msg.sub[c].port
		strAD = gb_msg.sub[c].address
		for s in SubList:
			if s.compareSub(ID,DT,intPT,StrAD):
				#already exists in list
				break
			else:
				#build sub
				newsub = Subscriber.Subscriber(DT,ID,intPT,strAD)
				#add to list
				SubList.append(newsub)
				break
		#end sublist check
	#end all possible subs
	return SubList
	
def updateSubListFromNetwork(pkt,SubList):
	#get the data string from the packet
	data_str = str(pkt.getData())
	#parse into type using protobuf
	gb_msg = PyPackets_pb2.NMHeartBeat()
	gb_msg.ParseFromString(data_str)
	#loop through subs in heartbeat
	for c in len(gb_msg.sub):
		ID = bytearray(gb_msg.sub[c].id)
		DT = bytearray(gb_msg.sub[c].datatype)
		intPT = gb_msg.sub[c].port
		strAD = gb_msg.sub[c].address
		for s in SubList:
			if s.compareSub(ID,DT,intPT,StrAD):
				#already exists in list
				break
			else:
				#build sub
				newsub = Subscriber.Subscriber(DT,ID,intPT,strAD)
				#add to list
				SubList.append(newsub)
				break
		#end sublist check
	#end all possible subs
	return SubList

def checkIfHeartBeat(pkt,SubList):
	if pkt.getDataType() == PyPacket.PacketDataType.PKT_NETWORK_MANAGER_HEARTBEAT:
		#parse the heartbeat
		print 'Received Network Manager Heartbeat'
		return True
	elif pkt.getDataType() == PyPacket.PacketDataType.PKT_NODE_HEARTBEAT:
		#parse the heartbeat
		print 'Received Node Heartbeat'
		SubList = updateSubListFromNode(pkt,SubList)
		return True
	else:
		print 'Not Heartbeat'
		return False
	


#=============
# Main Loop
#=============

#Test Code
pkt_id = PyPacket.PacketID(PyPacket.PacketPlatform.AIRCRAFT,10)
newPacket = PyPacket.PyPacket()
newPacket.setDataType(PyPacket.PacketDataType.PKT_NETWORK_MANAGER_HEARTBEAT)
newPacket.setID(pkt_id.getBytes())
newPacket.setData('Testing Network Manager')
#newPacket.displayPacket()

msg = newPacket.getPacket()
#print PyPacket.printByteArrayInHex(bytearray(PyPacket.PacketDataType.PKT_NETWORK_MANAGER_HEARTBEAT))

pkt_id = PyPacket.PacketID(PyPacket.PacketPlatform.DUMMY,11)
newTPkt = PyPacket.PyPacket()
newTPkt.setDataType(PyPacket.PacketDataType.PKT_DMY_MSG)
newTPkt.setID(pkt_id.getBytes())


#Subscriber List
SubscriberList = []
#SubscriberList.append(Subscriber.Subscriber(newPacket.getDataType(),newPacket.getID(),16000,'localhost'))
#subA = Subscriber.Subscriber(PyPacket.PacketDataType.PKT_DMY_MSG,PyPacket.PacketID(PyPacket.PacketPlatform.DUMMY,11).getBytes(),10000,'localhost')
#subA = Subscriber.Subscriber(newTPkt.getDataType(),newTPkt.getID(),10000,'localhost')
#SubscriberList.append(subA)

#~!!~ There is an issue comparing the results that come from the packet to the CONSTANTS that define it.
#subB = Subscriber.Subscriber(PyPacket.PacketDataType.PKT_DMY_MSG,PyPacket.PacketID(PyPacket.PacketPlatform.DUMMY,10).getBytes(),11000,'localhost')
#SubscriberList.append(subB)
# for sb in SubscriberList:
	# sb.printSubInfo()

RECV_BUFF = 8192

OWNIP = socket.gethostname() # ~!!~ doesn't work
PORT = 16000

Servants = ['localhost']

#Create my UDP Listening Socket
manager_in_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
manager_in_socket.setblocking(0)
manager_in_socket.bind(('',16000))

#Create my UDP Sending Socket
manager_out_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
manager_out_socket.setblocking(0)

#Put them into lists
inputs = [manager_in_socket]
outputs = [manager_out_socket]

#message_queues = {} #TBD
message_queues = Queue.Queue()
# for o in outputs:
	# message_queues[o].Queue.Queue()
	
#message_queues.put([('localhost',16000), msg])

count = 0

Quit = False

print 'Starting!'
print time.time()
start = time.time()
while not Quit:
	print >>sys.stderr, '\nwaiting for the next event'
	readable, writable, exceptional = select.select(inputs, outputs, inputs)
	
	#Handle Inputs
	for s in readable:
		#Get data from socket
		dataPkt, address = s.recvfrom(RECV_BUFF)
		print >>sys.stderr, 'recieved "%s" from %s' %(len(dataPkt), address)
		#Assign datapkt as an object
		newPkt = PyPacket.PyPacket()
		newPkt.setPacket(dataPkt)
		#newPkt.displayPacket()
		#Forward the packet into the correct queues
		heartbeat = checkIfHeartBeat(newPkt)
		if not heartbeat:
			print('forwarding packet')
			message_queues = forwardPacket(newPkt,message_queues,SubscriberList)
		#Print relevance for debug
		
	for s in writable:
		try:
			next_msg = message_queues.get_nowait()
		except Queue.Empty:
			print >>sys.stderr, 'Output queue is empty'
			time.sleep(.5)
		else:
			s.sendto(next_msg[1],next_msg[0])
			#time.sleep(.5)
			print 'Sent message from que'
		# if s is manager_out_socket:
			# for a in Servants:
				# #build message
				# message = 'Test'
				# #send to address of Servant
				# s.sendto(message,(a,PORT))
				
	#time.sleep(1)
	#count +=1
	#print count
	if (start - time.time()) >= 30:
		Quit = True
#End of While Loop
print 'Closing Sockets'
for s in inputs:
	s.close()
for s in outputs:
	s.close()

print time.time()
print 'Finished: Ending'
