import sys
sys.path.insert(0,'./protobuf')
import PyPacket
import PyPacketLogger
import PyPackets_pb2
from google.protobuf import json_format


name = "Aircraft_AC50_Sensing_Task_Log_001.pypl"
myPacketLogger = PyPacketLogger.PyPacketLogger()
myPacketLogger.openLogFile(name,True)
