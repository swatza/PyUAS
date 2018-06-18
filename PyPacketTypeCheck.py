#PyUAS Lib
import PyPacket

def isAutoPilotPixhawkMsg(pkt):
    if pkt.getDataType() == PyPacket.PacketDataType.PKT_AUTOPILOT_PIXHAWK:
        return True
    else:
        return False

def isWaypointMsg(pkt):
    if pkt.getDataType() == PyPacket.PacketDataType.PKT_WAYPOINT:
        return True
    else:
        return False

def isRFLearnCmd(pkt):
    if pkt.getDataType() == PyPacket.PacketDataType.PKT_RF_LEARN_CMD:
        return True
    else:
        return False

def isRFDataMsg(pkt):
    if pkt.getDataType() == PyPacket.PacketDataType.PKT_RF_DATA_MSG:
        return True
    else:
        return False

