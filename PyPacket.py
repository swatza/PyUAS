'''
The PYPACKET for wrapping google buffer messages in communication streams by indicating the type of data contained within 
the string. At this layer, the Packet Data Type and PacketID allows for easy analysis and forwarding of the packet to
the correct process/program running on the device or to another device. 

Packet Header Format
-----------------------
PacketDataType [1 Bytes] -> 0 - 255
PacketID [3 Bytes]
    PacketPlatform [2 Bytes] -> String 
    PacketIdentifier [1 Byte] -> Number 0 - 255 ~!!~ Fix me for easy use in mapping outputs
-----------------------
PacketData [N Bytes] -> Serialized Google buffer string (protobuf)
-----------------------
'''

import sys
from struct import *
from google.protobuf import text_format

sys.path.insert(0, './protobuf')
import PyPackets_pb2

RECVBUFF = 8192 #65536 #8192


# TODO: Set the packet to be in a specific binary format (Little Endian)

def printByteArrayInHex(array):
    str = '0x'
    for a in array:
        s = hex(a)
        List = s.split('x')
        str = str + List[1]
    return str

# Enumeration of the Packet Types for simplicity using Hexadecimal
# POSSIBLE NAMING COLLISION WITH CURRENT SETUP (two of the same data types being produced by 1 vehicle = same ID but different internal data)
class PacketDataType:
    # GCS Messages
    PKT_GCS_CMD = pack('b', 01)
    # Aircraft State Msgs
    PKT_AUTOPILOT_PIXHAWK = pack('b', 02)
    # Network Messages
    PKT_NETWORK_MANAGER_HEARTBEAT = pack('b', 10)  # [0x0,0x0] #0x00
    PKT_NODE_HEARTBEAT = pack('b', 11)
    PKT_NETWORK_MANAGER_STATUS = pack('b', 12)
    PKT_DMY_MSG = pack('b', 13)
    # RF comm-aware project
    PKT_RF_DATA_MSG = pack('b', 14)
    PKT_RF_PL_MAP_MSG = pack('b', 15)
    PKT_RF_STACKED_MAP_MSG = pack('b', 16)
    PKT_RF_LEARN_CMD = pack('b',19)
    # More will be added
    PKT_WAYPOINT = pack('b', 17)
    PKT_WAYPOINT_LIST = pack('b', 18)
    # Balloon Msgs
    PKT_BALLOON_SENSOR_MSG = pack('b', 30)
    PKT_BALLOON_SENSOR_SET = pack('b', 31)
    # IRISS Wrapper
    PKT_IRISS_WRAPPER_MSG = pack('b', 32)  # wrap an iriss packet with my packet
    # JSON Wrapper
    PKT_JSON_STRING = pack('b',33)


# Creation of a PacketID that is used for identifying where a packet source
class PacketID:
    def __init__(self, platform, identifer):
        self.P = platform  # PacketPlatform
        self.I = identifer  # PacketIdentifer

    def getBytes(self):
        bytesOut = bytearray(self.P)
        bytesOut.append(self.I)
        return bytesOut

    def getPlatform(self):
        return self.P #TODO! is this right?

    def getIdentifier(self):
        return self.I #TODO! is this right?

# Enumeration of the Packet Platforms for simplicity
class PacketPlatform:
    AIRCRAFT = 'AC'
    GROUND_CONTROL_STATION = 'GS'
    SERVER_STATION = 'SS'
    COMMAND_AND_CONTROL_STATION = 'CC'
    DUMMY = 'DM'
    BALLOON = 'BL'
    
class PyPacket(object):
    
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.packet = bytearray(0) #Zero the byte array
    
    '''
    Get and Set Full Packet
    '''
    def getPacket(self):
        return self.packet
        
    def setPacket(self, pkt):
        self.packet = bytearray(pkt)
        
    def getPacketSize(self):
        p = self.getPacket()
        return len(p)
    
    '''
    Get and Set the Packet Data Type
    '''
    def getDataType(self):
        return self.packet[0:1]
        
    def setDataType(self, byteA):
        if len(self.packet) == 0:
            self.packet.append(byteA)
        else:
            self.packet[0] = byteA
    '''
    Get and Set the Packet Identifier
    '''

    def getID(self):
        return self.packet[1:4]

    def setID(self, bytesIn):
        if len(self.packet) == 0:
            #Add an empty byte for the datatype
            self.packet.append(pack('b',0))
            for r in range(3):
                # TODO! Fix me
                self.packet.append(bytesIn[r])
        elif len(self.packet) == 1:
            for r in range(3):
                # TODO! Fix me
                self.packet.append(bytesIn[r])
        else:
            self.packet[1] = bytesIn[0]
            self.packet[2] = bytesIn[1]
            self.packet[3] = bytesIn[2]

    '''
    Get and Set the Packet Data 
    '''
    def getData(self):
        if len(self.packet) > 4:
            return self.packet[4:len(self.packet)]
        else:
            return None
            
    def clearData(self):
        #copy id and datatype
        copyOfId = self.getID()
        copyOfDT = self.getDataType()
        #clear byte array
        self.reset()
        #replace
        self.setDataType(str(copyOfDT))
        self.setID(copyOfId)
        #self.displayPacket()
        
    def setData(self, d):
        if len(self.packet) > 4:
            # Copy over the old parts
            self.clearData()
            # TODO! Change me
            #del self.packet[4:len(self.packet)] Old Method
        for i in range(len(d)):
            self.packet.append(d[i])

    def getDataSize(self):
        d = self.getData()
        if d:
            return len(d)
        else:
            return 0

    def printData(self):
        data = self.getData()
        if self.getDataType() == PacketDataType.PKT_DMY_MSG:
            msg = PyPackets_pb2.dummy_msg()
            msg.ParseFromString(str(data))
            return text_format.MessageToString(msg)
        elif self.getDataType() == PacketDataType.PKT_NODE_HEARTBEAT:
            msg = PyPackets_pb2.NodeHeartBeat()
            msg.ParseFromString(str(data))
            return text_format.MessageToString(msg)
        else:
            return 'No known data type'

    def displayPacket(self):
        print 'Type = ', printByteArrayInHex(self.getDataType())
        # printByteArrayInHex(self.getDataType())
        print 'ID = ', printByteArrayInHex(self.getID())
        print 'Data:', self.printData()
        print 'Size = ', self.getDataSize()
        print 'Total Size = ', self.getPacketSize()

'''
Dictionary Dispatch Lookup for DataType and the Protobuf msg creation
'''


def getNMStatus():
    return [PyPackets_pb2.NMStatus(), 'NMStatus']

def getNMHeartBeat():
    return [PyPackets_pb2.NMHeartBeat(), 'NMHeartBeat']

def getGCSCommand():
    return Null

def getNodeHeartBeat():
    return [PyPackets_pb2.NodeHeartBeat(), 'NodeHeartBeat']

def getDummy():
    return [PyPackets_pb2.dummy_msg(), 'DummyMsg']

def getAircraftPixhawkState():
    return [PyPackets_pb2.AircraftPixhawkState(), 'AircraftPixhawkState']

def getRF_PL_Map_Msg():
    return [PyPackets_pb2.RF_PL_Map_Msg(), 'RF_PL_Map_Msg']

def getRF_Data_Msg():
    return [PyPackets_pb2.RF_Data_Msg(), 'RF_Data_Msg']

def getRF_Learn_Cmd():
    return [PyPackets_pb2.RF_Learn_Cmd(), 'RF_Learn_Cmd']

def getRF_Stacked_Map_Msg():
    return [PyPackets_pb2.RF_Stacked_Map_Msg, 'RF_Stacked_Map_Msg']

def getBalloon_Sensor_Msg():
    return [PyPackets_pb2.Balloon_Sensor_Msg(), 'Balloon_Sensor_Msg']

def getBalloon_Sensor_Set_Msg():
    return [PyPackets_pb2.Balloon_Sensor_Set_Msg(), 'Balloon_Sensor_Set_Msg']

def getIRISS_Wrapper():
    return [PyPackets_pb2.IRISS_Wrapper(), 'IRISS_Wrapper']

TypeDispatch = {
    str(PacketDataType.PKT_NETWORK_MANAGER_STATUS): getNMStatus,
    str(PacketDataType.PKT_NETWORK_MANAGER_HEARTBEAT): getNMHeartBeat,
    str(PacketDataType.PKT_GCS_CMD): getGCSCommand,
    str(PacketDataType.PKT_DMY_MSG): getDummy,
    str(PacketDataType.PKT_NODE_HEARTBEAT): getNodeHeartBeat,
    str(PacketDataType.PKT_AUTOPILOT_PIXHAWK): getAircraftPixhawkState,
    str(PacketDataType.PKT_RF_DATA_MSG): getRF_Data_Msg,
    str(PacketDataType.PKT_RF_PL_MAP_MSG): getRF_PL_Map_Msg,
    str(PacketDataType.PKT_RF_LEARN_CMD): getRF_Learn_Cmd,
    str(PacketDataType.PKT_RF_STACKED_MAP_MSG): getRF_Stacked_Map_Msg,
    str(PacketDataType.PKT_BALLOON_SENSOR_MSG): getBalloon_Sensor_Msg,
    str(PacketDataType.PKT_BALLOON_SENSOR_SET): getBalloon_Sensor_Set_Msg,
    str(PacketDataType.PKT_IRISS_WRAPPER_MSG): getIRISS_Wrapper
}

def getAircraftPlatform():
    return PacketPlatform.AIRCRAFT
def getBalloonPlatform():
    return PacketPlatform.BALLOON
def getGCSPlatform():
    return PacketPlatform.GROUND_CONTROL_STATION
def getServerPlatform():
    return PacketPlatform.SERVER_STATION
def getCommandPlatform():
    return PacketPlatform.COMMAND_AND_CONTROL_STATION
def getDummyPlatform():
    return PacketPlatform.DUMMY

#Set the string to all lowercase for casting into the dictionary
def formatPlatformString(string):
    return string.lower()

PlatformDispatch = {
    str("aircraft"): getAircraftPlatform,
    str("balloon"): getBalloonPlatform,
    str("groundstation"): getGCSPlatform,
    str("server"): getServerPlatform,
    str("command"): getCommandPlatform,
    str("dummy"): getDummyPlatform
}
