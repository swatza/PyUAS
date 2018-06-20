
#General Lib
import time

#PyUAS Lib
import PyPacket
import PyPackets_pb2
import Subscriber

def buildRFLearnCommand(my_id, packet_counter,node_list_to_learn, node_list_to_plan,waypoint_flag,mode_string):
    #Create the packet
    pkt = PyPacket.PyPacket()
    pkt.setDataType(PyPacket.PacketDataType.PKT_RF_LEARN_CMD)
    pkt.setID(my_id.getBytes())
    #Create the message
    msg = PyPackets_pb2.RF_Learn_Cmd()
    #Store the header information
    msg.packetNum = packet_counter
    msg.ID = str(pkt.getID())
    msg.time = time.time()
    #store message specific items
    msg.NodesToLearn.extend(node_list_to_learn)
    msg.NodesToPlan.extend(node_list_to_plan)
    msg.calculateWaypointFlag = waypoint_flag
    msg.mode = mode_string
    #Serialize and store
    data_str = msg.SerializeToString()
    pkt.setData(data_str)
    del msg
    return pkt.getPacket()

def buildNodeHeartBeat(my_id, subscribers, packet_counter):
    # Create the packet
    pkt = PyPacket.PyPacket()
    pkt.setDataType(PyPacket.PacketDataType.PKT_NODE_HEARTBEAT)
    pkt.setID(my_id.getBytes())
    #Create the message
    msg = PyPackets_pb2.NodeHeartBeat()
    # Store the header information
    msg.packetNum = packet_counter
    msg.ID = str(pkt.getID())
    msg.time = time.time()
    #Add all the subscriber info
    c = 0
    for n in subscribers:
        new = msg.sub.add()
        new.id = str(n.ID)
        new.datatype = str(n.TYPE)
        new.port = n.PORT
        new.address = n.IP
        new.msgfreq = n.FREQ
        c += 1
    #END LOOP
    # Serialize and store
    data_str = msg.SerializeToString()
    pkt.setData(data_str)
    del msg
    return pkt.getPacket()

def buildNMStatusMessage(my_id,sublist,packet_counter,total_msgs,since_last_msgs,avg_delay,size_of_que):
    # Create the packet
    pkt = PyPacket.PyPacket()
    pkt.setDataType(PyPacket.PacketDataType.PKT_NETWORK_MANAGER_STATUS)
    pkt.setID(my_id.getBytes())
    # Create the message
    msg = PyPackets_pb2.NMStatus()
    # Store the header information
    msg.packetNum = packet_counter
    msg.ID = str(pkt.getID())
    msg.time = time.time()
    # List of the local subscribers
    for s in sublist:
        new = msg.subs.add()
        new.id = s.ID
        new.datatype = s.TYPE
        new.port = s.PORT
        new.address = s.IP
        new.msgfreq = s.FREQ
    #Add in other information
    msg.messagesInQue = size_of_que
    msg.numberOfLocalSubscribers = len(sublist)
    msg.numberOfMsgs = since_last_msgs
    msg.totalMsgsRecv = total_msgs
    msg.avgTimeDelay = avg_delay   # Delay between received and sent
    # Serialize and store
    data_str = msg.SerializeToString()
    pkt.setData(data_str)
    del msg
    return pkt.getPacket()

def buildNMHeartBeat(my_id,sublist,nmlist,packet_counter,my_ip,my_port):
    # Create the packet
    pkt = PyPacket.PyPacket()
    pkt.setDataType(PyPacket.PacketDataType.PKT_NETWORK_MANAGER_HEARTBEAT)
    pkt.setID(my_id.getBytes())
    # Create the message
    msg = PyPackets_pb2.NMHeartBeat()
    msg.ID =str(my_id.getBytes())
    msg.packetNum = packet_counter
    msg.time = time.time()
    # add local subscribers
    for s in sublist:
        new = msg.sub.add()
        new.id = str(s.ID)
        new.datatype = str(s.TYPE)
        new.port = my_port  # my port
        new.address = my_ip  # my IP
        new.msgfreq = s.FREQ
    # end loop
    # add network managers
    for nm in nmlist:
        new = msg.nms.add()
        new.IP = nm[0]
        new.PORT = str(nm[1])
    # end loop
    # Serialize and store
    data_str = msg.SerializeToString()
    pkt.setData(data_str)
    del msg
    return pkt.getPacket()