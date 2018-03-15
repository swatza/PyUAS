

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


def printByteArrayInHex(array):
	str = '0x'
	for a in array:
		s = hex(a)
		List = s.split('x')
		str = str + List[1]
	return str

#Enumeration of the Packet Types for simplicity using Hexadecimal
class PacketDataType:
	PKT_NETWORK_MANAGER_HEARTBEAT = pack('b',10)#[0x0,0x0] #0x00
	PKT_NODE_HEARTBEAT = pack('b',11)
	PKT_DMY_MSG = pack('b',12)
	#More will be added
	
#Creation of a PacketID that is used for identifying where a packet source
class PacketID:
	def __init__(self, platform, identifer):
		self.P = platform #PacketPlatform
		self.I = identifer #PacketIdentifer
		
	def getBytes(self):
		bytesOut = bytearray(self.P)
		bytesOut.append(self.I)
		return bytesOut
	
#Enumeration of the Packet Platforms for simplicity 
class PacketPlatform:
	AIRCRAFT = 'AC'
	GROUND_CONTROL_STATION = 'GS'
	SERVER_STATION = 'SS'
	COMMAND_AND_CONTROL_STATION = 'CC'
	DUMMY = 'DM'
	
	
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
		if len(self.packet) == 1:
			for r in range(3):
				self.packet.append(bytesIn[r])
		else:
			self.packet[1] = bytesIn[0];
			self.packet[2] = bytesIn[1];
			self.packet[3] = bytesIn[2];
			
	'''
	Get and Set the Packet Data 
	'''
	def getData(self):
		if len(self.packet) > 4:
			return self.packet[4:len(self.packet)]
		else:
			return 
		
	def setData(self, d):
		for i in range(len(d)):
			self.packet.append(d[i])
	
	def getDataSize(self):
		d = self.getData()
		if d:
			return len(d)
		else:
			return 0
		
	def displayPacket(self):
		print 'Type = ', printByteArrayInHex(self.getDataType())
		#printByteArrayInHex(self.getDataType())
		print 'ID = ', printByteArrayInHex(self.getID())
		print 'Size = ', self.getDataSize()
		print 'Total Size = ', self.getPacketSize()
		