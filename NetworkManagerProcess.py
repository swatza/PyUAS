'''
Author: Spencer Watza

Network Manager Independent Process

Summary: This program will run on a machine to manage routing and other information. 

Design 1: All communication routes through this process with outgoing/incoming messages being forwarded
Design 2: This process just maintains the information about who is routing to who so systems don't need to know 
everyone's details in maps of publish-subscribe format


Notes: All Network Managers are listening and sending out on Port 16000 to each other with UDP protocol

'''
#Imports 
import socket
import sys
import select
import time
import Queue

sys.path.insert(0, './protobuf')
import PyPackets_pb2

import PyPacket
import Subscriber


RECV_BUFF = 8192
#============
# Functions
#============

def parsePacket(pkt,SubList):
    """Determines which subscribers to forward the pypacket to.
    
    Using a list of subscribers, this function loops through and determines all possible subscribers that would
    be interested in receiving this packet. The system checks the ID and datatype as well as the frequency rate 
    that the subscriber requests
    
    Args:
        arg1 (PyPacket): A PyPacket Object that needs to be forwarded
        arg2 (List<Subscriber>): A List of Subscribers that the manager knows of
    Returns:
        List<Subscriber>: List of subscribers that the packet needs to be forwarded to
    """
    #print the packet
    #pkt.displayPacket()
    #get the data type
    data_type = pkt.getDataType()
    #get the identifier
    identifier = pkt.getID()
    #check for subscribers internal and external
    sendList = []
    currentTime = time.time()
    for s in SubList:
        #check for the correct sub
        if s.TYPE == data_type:
            if s.ID == identifier:
                #Check the request rate
                if((currentTime - s.getLastTime()) >= s.getRequestTime()):
                    s.setLastTime(currentTime) #update the last time it was sent
                    sendList.append(s) #Add it to the list
    #Return send list
    return sendList

def forwardPacket(pkt, out_socket_queues,SubList,recvtime):
    """ Loops through the list of subscribers to send the packet to and its to the out queue
    
    Forward packet takes the packet and list of subscribers to send to. It grabs the address of the subscriber
    and adds the packet and the address to teh output queue. T
    
    Args:
        arg1 (PyPacket): A pypacket object that needs to be forwarded
        arg2 (Queue): Queue for sending messages
        arg3 (List<Subscriber>): A list of subscribers taht need to get hte packet
    Returns:
        Queue: Messages that were added to the queue
    """
    sList = parsePacket(pkt,SubList) #figured out who to send the packet to
    #for every address in the list, add it to the correct queue
    for c in sList:
        out_socket_queues.put([c.getAddress(),pkt.getPacket(),recvtime])
    return out_socket_queues

def createNMHBMessage(sublist,nmlist, counter, MYID, MYIP, MYPORT):
    msg = PyPackets_pb2.NMHeartBeat()
    msg.packetNum = counter
    msg.ID = MYID
    msg.time = time.time()
    #add local subscribers
    for s in sublist:
        new = msg.sub.add()
        new.id = str(s.id)
        new.datatype = str(s.TYPE)
        new.port = MYPORT #my port
        new.address = MYIP #my IP
        new.msgfreq = s.FREQ
    #end loop
    #add network managers
    for nm in nmlist:
        new = msg.nms.add()
        new.IP = nm[0]
        new.PORT = nm[1]
    #end loop
    data_str = msg.SerializeToString()
    return data_str 

def createNMStatusMessage(sublist,counter, MYID, totalMsgs, sincelastMsgs, avgdelay, sizeOfQue):
    msg = PyPackets_pb2.NMStatus()
    msg.packetNum = counter
    msg.ID = MYID.getBytes()
    msg.time = time.time()
    #List of the local subscribers
    for s in sublist:
        new = msg.subs.add()
        new.id = s.ID
        new.datatype = s.TYPE
        new.port = s.PORT
        new.address = s.IP
        new.msgfreq = s.FREQ
    #list of the local publishers???
    #Size of Queue
    msg.messagesInQue = sizeOfQue
    msg.numberOfLocalSubscribers = len(sublist)
    #Number of messages sent since last time
    msg.numberOfMsgs = sincelastMsgs
    msg.totalMsgsRecv = totalMsgs
    #Delay between received and sent
    msg.avgTimeDelay = avgdelay
    data_str = msg.SerializeToString()
    #magic
    return data_str

"""
Updates from a node (aka a process)
"""
def updateSubListFromNode(pkt,SubList):
    #get the data string from the packet
    data_str = str(pkt.getData())
    #parse into type using protobuf
    gb_msg = PyPackets_pb2.NodeHeartBeat()
    gb_msg.ParseFromString(data_str)
    #loop through subs in heartbeat
    for c in gb_msg.sub:
        ID = bytearray(str(c.id))
        DT = bytearray(str(c.datatype))
        intPT = c.port
        strAD = c.address
        freq = c.msgfreq
        included = False
        for s in SubList:
            if s.compareSub(ID,DT,intPT,strAD):
                #already exists in list
                included = True
                break
            else:
                included = False
        #end sublist check
        #Check
        if not included:
            #build sub
            newsub = Subscriber.Subscriber(DT,ID,intPT,strAD,freq)
            #add to list
            SubList.append(newsub)
    #end all possible subs
    return SubList

"""
Takes the packet, parses the information about other subscribers from another Network Manager,
Adds them to the list of subscribers. 
"""
def updateSubListFromNetwork(pkt,SubList):
    #get the data string from the packet
    data_str = str(pkt.getData())
    #parse into type using protobuf
    gb_msg = PyPackets_pb2.NMHeartBeat()
    gb_msg.ParseFromString(data_str)
    #loop through subs in heartbeat
    for c in gb_msg.sub:
        ID = bytearray(str(c.id))
        DT = bytearray(str(c.datatype))
        intPT = c.port
        strAD = c.address
        freq = c.msgfreq
        included = False
        for s in SubList:
            if s.compareSub(ID,DT,intPT,strAD):
                #already exists in list
                included = True
                break
            else:
                included = False
        #end sublist check
        #Check
        if not included:
            #build sub
            newsub = Subscriber.Subscriber(DT,ID,intPT,strAD,freq)
            #add to list
            SubList.append(newsub)
    #end all possible subs
    return SubList

"""
Takes the local subscribers and adds those to global list if it doesn't have them included 
FUTURE OPTIMIZATION: Only check for new subscribers not all of them
"""
def updateTotalSubList(SubListLocal,SubListGlobal):
    for sl in SubListLocal:
        ID = sl.ID
        DT = sl.TYPE
        intPT = sl.PORT
        strAD = sl.IP
        included = False
        for sg in SubListGlobal:
            if sg.compareSub(ID,DT,intPT,strAD):
                #alread exists in list
                included = True
                break
            else:
                included = False
        #Check
        if not included:
            SubListGlobal.append(sl)
    #End of Loop
    return SubListGlobal
    
def calculateAvgTimeDelay(delayList):
    #Loop through and sum
    sum = 0
    for i in delayList:
        sum += i
    return sum/len(delayList)

#=============
# Main Loops
#=============

#The ID 
#Generate the ID for this Network Manager (should be loaded from arguments/file)
id = PyPacket.PacketID(PyPacket.PacketPlatform.GROUND_CONTROL_STATION,00)

#Predefine the Network Manager HeartBeat Message
nmhb_pkt = PyPacket.PyPacket()
nmhb_pkt.setDataType(PyPacket.PacketDataType.PKT_NETWORK_MANAGER_HEARTBEAT)
nmhb_pkt.setID(id.getBytes())
#Predefine the Network Status Message
nmsm_pkt = PyPacket.PyPacket()
nmsm_pkt.setDataType(PyPacket.PacketDataType.PKT_NETWORK_MANAGER_STATUS)
nmsm_pkt.setID(id.getBytes())

#Subscriber Lists
SubscriberListInternal = [] #Only local subscribers of this network manager
SubscriberListFull = [] #all subscribers in the entirity of the network

#Network Managers
NetworkManagerList = [] #all the IPs of the network managers
NetworkManagerList.append(['localhost',16000]) #this should be correct

#Hardcoded for now
PORT = 16000
MYPORT = PORT
MYIP = 'localhost'

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
    
#message_queues.put([('localhost',16000), msg]) example how the message is stored in que

Quit = False
deltaT_status = 0
deltaT_nmhb = 0
lastT_status = time.time()
lastT_nmhb = time.time()
status_msg_rate = 5
nmhb_msg_rate = 10
nmhb_counter = 0
status_counter = 0

total_messages_recieved = 0 #total number of msgs
messages_recieved = 0 #how many messages have we recieved since last reset
time_delay = [] #how long the message sits in the Network Manager
recvtime = 0.0

print 'Starting!'
currentTime = time.time()
print currentTime

while not Quit:
    try:
        #Is it time to send a network heart beat message
        if (deltaT_nmhb >= nmhb_msg_rate):
            #if the internal list isn't empty
            if (len(SubscriberListInternal) > 0 and len(NetworkManagerList) > 0):
                #create the message
                nmhb_counter += 1 #increment counter 
                msg_str = createNMHBMessage(SubscriberListInternal,NetworkManagerList,nmhb_counter,id,MYIP,MYPORT)
                #add this message to the packet
                nmhb_pkt.setData(msg_str)
                #loop through the network manager list
                for nm in NetworkManagerList:
                    #add each NM target and message contents to the queue
                    message_queues.put([(nm[0],nm[1]),nmhb_pkt.getPacket()])
                #Remove the message from packet
        
        #Is it time to send a network status message
        if (deltaT_status >= status_msg_rate):
            #if there is a subscriber for this message
            status_counter += 1 #increment counter
            total_messages_recieved += messages_recieved
            #calculate avg time delay
            delay = calculateAvgTimeDelay(time_delay)
            #Get size of que
            size = message_queues.qsize()
            #Create the msg str
            msg_str = createNMStatusMessage(SubscriberListInternal,status_counter,id,total_messages_recieved,messages_recieved,delay,size)
            #add to the packet
            nmsm_pkt.setData(msg_str)
            messages_recieved = 0 #rest
            #list of subscribers whow ant this message
            for s in SubscriberListFull:
                if s.TYPE == PyPacket.PacketDataType.PKT_NETWORK_MANAGER_STATUS:
                    if s.ID == id:
                        #add it to the que
                        message_queues.put([s.getAddress(),nmsm_pkt.getPacket(),recvtime])
            #end for loop
        #end msg generation loop
            
        #print >>sys.stderr, '\nwaiting for the next event'
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        #Handle Inputs
        for s in readable:
            #Get data from socket
            dataPkt, address = s.recvfrom(RECV_BUFF)
            #Add in time received (so that way we can track delay between in/out of messages
            recvtime = time.time()
            print >>sys.stderr, 'recieved "%s" from %s' %(len(dataPkt), address)
            #increment messages recieved
            messages_recieved += 1
            #Assign datapkt as an object
            newPkt = PyPacket.PyPacket()
            newPkt.setPacket(dataPkt)
            #newPkt.displayPacket()
            #Forward the packet into the correct queues
            if (newPkt.getDataType() == PyPacket.PacketDataType.PKT_NETWORK_MANAGER_HEARTBEAT):
                print 'Received Network Manager Heartbeat'
                #add the information to our full subscriber list 
                SubscriberListFull = updateSubListFromNetwork(newPkt, SubscriberListFull)
            elif (newPkt.getDataType() == PyPacket.PacketDataType.PKT_NODE_HEARTBEAT):
                print 'Recieved Node Heartbeat'
                #add the information to our local subscriber list
                SubscriberListInternal = updateSubListFromNode(newPkt, SubscriberListInternal)
                #Then update the full subscriber list
                SubscriberListFull = updateTotalSubList(SubscriberListInternal,SubscriberListFull)
            else:
                print('forwarding packet')
                message_queues = forwardPacket(newPkt,message_queues,SubscriberListFull,recvtime)
        #Handle Outputs
        for s in writable:
            try:
                next_msg = message_queues.get_nowait()
            except Queue.Empty:
                time.sleep(.01)
            else:
                s.sendto(next_msg[1],next_msg[0])
                time_delay.append(time.time() - next_msg[2])

    except (KeyboardInterrupt, SystemExit):
        Quit = True
        print 'Closing Sockets'
        for s in inputs:
            s.close()
        for s in outputs:
            s.close()
#End of While Loop
print time.time()
print 'Finished: Ending'