#Imports
import urllib2
import base64
import sys
import time
import threading
import json

sys.path.insert(0, '../PyUAS')  # get the path to the PyUAS Folder
sys.path.insert(0, '../PyUAS/protobuf')  # get the path to the protobuf format

#PYUAS LIBS
import PyPacket
import PyPackets_pb2
import assorted_lib
import PyPacketMsgBuilds
import PyPacketTypeCheck
import PyUAS_Ardupilot_Mission_Manager
import mav_command_wrappers



class MicroHardLogging(threading.Thread):
    def __init__(self, microhard_str, my_id, logmode):
        #register authorization string
        base64string = base64.encodestring('%s:%s' % ('admin', 'gocubuffs')).replace('\n', '')
        #setup microhard string
        RequestStr = microhard_str
        #request urlib string
        self.request = urllib2.Request(RequestStr)
        self.request.add_header("Authorization", "Basic %s" % base64string)

        #Create logger
        self.logger = logging.getLogger("MicrohardTest:Sensing")
        self.logger.setLevel(logmode)
        my_handler = logging.StreamHandler()
        self.logger.addHandler(my_handler)
        self.logger.info("Microhard Sensing Task Started")

        #create packet logger
        self.packet_log = PyPacketLogger.PyPacketLogger( ('Vehicle_' + my_id.getPlatform() + str(my_id.getIdentifier()) + '_Microhard_Sensing_Log'))
        self.packet_log.initFile()
        self.logger.info("Logging Sensor Packets to %s:", self.packet_log.logname)

        #Store important parameters
        self.MYID = my_id

    def run(self):
        #pypacket
        mhPacket = PyPacket.PyPacket()
        newPacket.setDataType(PyPacket.PacketDataType.PKT_DMY_MSG)
        newPacket.setID(self.MYID.getBytes())

        #Protobuf message (just using dummy for strings right now)
        mh_data_msg = PyPackets_pb2.dummy_msg()
        mh_data_msg.ID = str(self.MYID.getBytes())

        #measurement timing variables
        last_measurement_time = 0
        measurement_rate = 1 #in Seconds]
        packet_counter = 1

        #Sensor run loop
        while not shutdown_event.is_set():
            #is it time to measure
            now_time = time.time()
            delta_time = now_time - last_measurement_time
            if delta_time > measurement_rate:
                self.logger.debug("Logging a new measurement")
                #Reset last time
                last_measurement_time = now_time
                #Get the response from radio
                response = urllib2(self.request)
                #INSERT WHATEVER YOU WANT TO GET FROM RADIO
                mh_data_msg.s = response

                #INSERT WHATEVER YOU WNAT FROM THE VEHICLE (Putting it into a json string
                json_obj = {}
                json_obj['lat'] = vehicle.location.global_frame.lat
                json_obj['lon'] = vehicle.location.global_frame.lon
                json_obj['alt'] = vehicle.location.global_relative_frame.alt
                json_obj['airspeed'] = vehicle.airspeed
                json_str = json.dumps(json_obj)

                mh_data_msg.s2 = json_str
                #store time of packet generation
                mh_data_msg.time = now_time
                #store and increment packet counter
                mh_data_msg.packetNum = packet_counter
                packet_counter += 1
                #Parse protobuf message
                data_str = mh_data_msg.SerializeToString()
                #Put data into packet
                mhPacket.setData(data_str)
                #Log packet
                self.packet_log.writePacketToLog(mhPacket)

        #End while loop
        self.logger.info("CLosing Sensor Task")
        print('\t Microhard Sensor Task [Closed]')




if __name__ == "__main__":
    #filler information
    home_lat = 40.00
    home_lon = -105.00
    base_altitude = 100 #meters
    #Connection to Ardupilot
    connection_string = '/dev/ttyS1' #Beaglebone setup
    apmm = PyUAS_Ardupilot_Mission_Manager.ArduPilotMissionManager(connection_string,"Testing Microhard Logging", base_altitude, [home_lat,home_lon])
    #Hand off the vehicle data stream
    vehicle = apmm.vehicle

    #Microhard string
    mh_str = "http://192.168.168.150/cgi-bin/webif/getradio.sh" #Make sure 192.168.168.1## matches aircraft number

    log_level = 10 #debug
    #My id
    my_id = PyPacket.PacketID(PyPacket.PacketPlatform.DUMMY,0)

    #start the microhard logging thread
    mhlogging = MicroHardLogging(mh_str,my_id,log_level)
    mhlogging.start()

    while threading.active_count() > 1:
        try:
            time.sleep(0.1)

        except(KeyboardInterrupt,SystemExit):
            #Exit
            shutdown_event.set()
    #End while
    print "Exiting"
    sys.exit()