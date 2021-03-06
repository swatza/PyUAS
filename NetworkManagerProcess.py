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
import PyPacketMsgBuilds
import PyPacketTypeCheck
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
    ''' Loops through the list of subscribers to send the packet to and its to the out queue
    
    Forward packet takes the packet and list of subscribers to send to. It grabs the address of the subscriber
    and adds the packet and the address to teh output queue. T
    
    Args:
        arg1 (PyPacket): A pypacket object that needs to be forwarded
        arg2 (Queue): Queue for sending messages
        arg3 (List<Subscriber>): A list of subscribers taht need to get hte packet
    Returns:
        Queue: Messages that were added to the queue
    '''
    sList = parsePacket(pkt,SubList) #figured out who to send the packet to
    #for every address in the list, add it to the correct queue
    for c in sList:
        out_socket_queues.put([c.getAddress(),pkt.getPacket(),recvtime])
    return out_socket_queues

"""
Check Sublist for since last heartbeat received and remove old ones that are over some threshold 
"""
def checkSubListForActiveListeners(SubList):
    heartbeat_threshold = 30 #30 seconds for now
    thisTime = time.time() # get current time stamp
    for sub in SubList:
        # Check the last time a heart beat was received
        if thisTime - sub.getLastHeartBeatTime() > heartbeat_threshold:
            #remove from sublist
            SubList.remove(sub)
            print 'Removed Subscriber'
            sub.printSubInfo() #should print out relevant information of the subscriber that was removed

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
                s.setLastHeartBeatTime(time.time())
                break
            else:
                included = False
        #end sublist check
        #Check
        if not included:
            #build sub
            newsub = Subscriber.Subscriber(DT,ID,intPT,strAD,freq)
            newsub.setLastHeartBeatTime(time.time())
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
                s.setLastHeartBeatTime(time.time())
                included = True
                break
            else:
                included = False
        #end sublist check
        #Check
        if not included:
            #build sub
            newsub = Subscriber.Subscriber(DT,ID,intPT,strAD,freq)
            newsub.setLastHeartBeatTime(time.time())
            #add to list
            SubList.append(newsub)
    #end all possible subs
    return SubList

"""
Takes the local subscribers and adds those to global list if it doesn't have them included 
TODO! FUTURE OPTIMIZATION: Only check for new subscribers not all of them
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

#Subscriber Lists
SubscriberListInternal = [] #Only local subscribers of this network manager
SubscriberListFull = [] #all subscribers in the entirity of the network

#Network Managers
NetworkManagerList = [] #all the IPs of the network managers
#This needs to be updated!! with a file or command line
NetworkManagerList.append(['192.168.168.156',16000]) #Talon 5

#Hardcoded for now
PORT = 16000
MYPORT = PORT
MYIP = '192.168.168.201' #Need to get my IP address

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
# for o in outputs: #if we split the networkmanager into multiple processes
    # message_queues[o].Queue.Queue()
    
#message_queues.put([('localhost',16000), msg]) example how the message is stored in que

Quit = False


deltaT_status = 0
lastT_status = time.time()
status_msg_rate = 5

deltaT_nmhb = 11
lastT_nmhb = time.time()
nmhb_msg_rate = 10

deltaT_check = 0
lastT_check = time.time()
check_rate = 5

#Message Counters
nmhb_counter = 0
status_counter = 0
total_messages_recieved = 0 #total number of msgs
messages_recieved = 0 #how many messages have we received since last reset
time_delay = [] #how long the message sits in the Network Manager
recvtime = 0.0

print 'Starting!'
currentTime = time.time()
print currentTime

while not Quit:
    try:
        #UPDATE deltaTs
        nowtime = time.time()
        deltaT_check = nowtime - lastT_check
        deltaT_nmhb = nowtime - lastT_nmhb
        #deltaT_status = nowtime - lastT_status
        #Check subscribers for inactive listeners based on previous heartbeat
        #TODO! run this at a lower frequency (like once a second or something or even less often
        if deltaT_check >= check_rate:
            checkSubListForActiveListeners(SubscriberListFull)
            lastT_check = time.time()
        #Is it time to send a network heart beat message
        if deltaT_nmhb >= nmhb_msg_rate:
            #if the internal list isn't empty
            lastT_nmhb = time.time()
            if (len(SubscriberListInternal) > 0 and len(NetworkManagerList) > 0):
                #create the message
                nmhb_counter += 1 #increment counter
                #(my_id,sublist,nmlist,packet_counter,my_ip,my_port)
                pkt_str = PyPacketMsgBuilds.buildNMHeartBeat(id,SubscriberListInternal,NetworkManagerList,nmhb_counter,MYIP,MYPORT)
                #loop through the network manager list
                for nm in NetworkManagerList:
                    #add each NM target and message contents to the queue
                    #(self.IP,self.PORT)
                    message_queues.put([(nm[0],nm[1]),pkt_str,time.time()])
                    print 'Sending NMHB to %s,%s'%(nm[0],nm[1])
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
            pkt_str = createNMStatusMessage(SubscriberListInternal,status_counter,id,total_messages_recieved,messages_recieved,delay,size)
            messages_recieved = 0 #rest
            #list of subscribers whow ant this message
            for s in SubscriberListFull:
                if s.TYPE == PyPacket.PacketDataType.PKT_NETWORK_MANAGER_STATUS:
                    if s.ID == id:
                        #add it to the que
                        message_queues.put([s.getAddress(),pkt_str,recvtime]) #TODO! This doesn't look right
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
            #print >>sys.stderr, 'recieved "%s" from %s' %(len(dataPkt), address)
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
                print 'Received Node Heartbeat'
                #add the information to our local subscriber list
                SubscriberListInternal = updateSubListFromNode(newPkt, SubscriberListInternal)
                #Then update the full subscriber list
                SubscriberListFull = updateTotalSubList(SubscriberListInternal,SubscriberListFull)
            else:
                #print('forwarding packet')
                message_queues = forwardPacket(newPkt,message_queues,SubscriberListFull,recvtime)
        #Handle Outputs
        for s in writable:
            while message_queues.qsize() > 0:
                try:
                    next_msg = message_queues.get_nowait()
                except Queue.Empty:
                    break;
                else:
                    s.sendto(next_msg[1],next_msg[0])
                    #self.logger.info("Message sent to: %s", ('localhost', self.NMPORT))
                    print'Sent Message to %s,%s' %(next_msg[0][0],next_msg[0][1]) #print out the port
                    time_delay.append(time.time() - next_msg[2])
                #End try
            #End While

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