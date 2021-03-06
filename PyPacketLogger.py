# imports
import time
import struct
import os
import logging
import sys
import array
import json

sys.path.insert(0, './protobuf')
import PyPacket
import PyPackets_pb2
from google.protobuf import json_format

class PyPacketLogger():
    # Time Stamp
    base_ext = '.pypl'
    base_name = 'pypacket_log'
    logname = 'pypacket_log_00.pypl'

    '''
    Instantiation of PyPacket
    '''

    def __init__(self, base_name=None):
        # Set the logger and other info
        if base_name:
            self.base_name = base_name  # set the value to be a predetermined name

        # create the logger
        self.logger = logging.getLogger("PyUAS:PyPacketLogger")
        self.logger.setLevel(logging.DEBUG)  # change this?
        self.packetbuffer = PyPacketBuffer()

    # Split in order to maintain opening/reading capability
    def initFile(self):
        # Increment file number and get full logname
        # CHANGE THIS SECTION
        fname = ''
        for i in range(0, 255):
            fname = self.base_name + '_%03d' % i + self.base_ext  # create the base value (3 decimals)
            if not os.path.isfile(fname):

                # Borrowed from Cory Dixon
                # delete the next higher number file if possible
                next_i = i + 1
                if next_i >= 256:
                    next_i = 0  # loop back around

                fname_next = self.base_name + '_%03d' % i + self.base_ext  # create the base value (3 decimals)
                # check if it exists
                if os.path.isfile(fname_next):
                    os.remove(fname_next)

                break

        # make sure we got a file
        if not fname:
            fname = self.base_name + '_00' + self.base_ext
            fname_next = self.base_name + '_01' + self.base_ext
            os.path.remove(fname)
            os.path.remove(fname_next)

        self.logname = fname

    def writePacketToLog(self, pypkt):
        # get the time stamp for log
        ts = time.time()
        startByte = 0xAA
        EndByte = 0xFF
        sb = struct.pack('b',startByte)
        eb = struct.pack('b',endByte)
        ts_str = struct.pack('<d', ts)  # little endian
        size = pypkt.getPacketSize()
        size_str = struct.pack('<L', size)
        # open binary file in append mode
        with open(self.logname, 'ab', 0) as outfile:
            outfile.write(sb)
            outfile.write(ts_str)  # write the time stamp
            outfile.write(size_str)  # write out the size of the data message (so we know where it ends)
            outfile.write(pypkt.getPacket())  # Write the data
            outfile.write(eb)
            outfile.flush()  # force the write to happen
            # COULD LOG SOMETHING
            return True  # error return that is was successful
        # Could log something
        return False  # error return that it failed to write

    def openLogFile(self, name, output_to_json_flag):
        if name:
            self.logname = name

        # open as binary for reading
        seekbyte = 0
        with open(self.logname, 'rb') as infile:
            # check to see if the seekbyte is at the end of file
            infile.seek(0, os.SEEK_END)
            length_of_file = infile.tell()
            #print length_of_file
            while (seekbyte+14) < length_of_file: #make sure there is atleast 14 bytes in the header
                #print seekbyte
                seekbyte = self.readPacketFromLog(infile, seekbyte) #Problem if the file isn't equal or something?
                #print "Read in packet from log"
        # We have finished reading in all the data
        if output_to_json_flag:
            print "Length is: %i" %self.packetbuffer.length
            # change the output to .json
            shortname = self.logname.split(".")[0]
            shortname = shortname + ".json"
            self.writeBufferToJson(shortname)

    def writeBufferToJson(self, filename_out):
        # open file
        with open(filename_out, 'w') as outfile:
            buffer_length = self.packetbuffer.getLengthOfBuffer()
            for i in range(0, buffer_length):
                # read in a buffer packet
                thispacket,timestamp = self.packetbuffer.getFromList(i)
                # determine the google message
                msg, thisType = PyPacket.TypeDispatch[str(thispacket.getDataType())]()
                # parse to google message
                msg.ParseFromString(thispacket.getData())
                # Parse to json
                json_obj = json_format.MessageToJson(msg)
                obj = json.loads(json_obj)
                json_string = json.dumps(obj) + '\n'
                outfile.write(json_string)
                #print 'wrote packet %i to json file' % i
            # end for loop
            print "Wrote %i Packets to json file" %i
        # End open

    def readPacketFromLog(self, readfile, location):
        # with an open file, read x bytes
        readfile.seek(location) #check the number of bytes left to read?
        #inBytes = readfile.read(1)
        #if struct.unpack('<b',inBytes)[0] == 0xAA:
        #    #start of the sequence; else we are miss aligned
        #    print "Packets are Aligned"
        #else:
        #    print "Misaligned Packets"
        # first read the 8 bytes for timestamp
        inBytes = readfile.read(8)
        #print len(inBytes)
        ts = struct.unpack('<d', inBytes)[0]
        # next read the 4 bytes for length of data
        inBytes = readfile.read(4)
        #print len(inBytes)
        dsize = struct.unpack('<L', inBytes)[0]
        #print dsize
        # read the data & create packet
        inBytes = readfile.read(dsize)
        #print len(inBytes)
        pkt = PyPacket.PyPacket()
        pkt.setPacket(inBytes)
        # add to the packet buffer
        self.packetbuffer.addtolist(pkt, ts)
        # calculate new location
        # inBytes = readfile.read(1) #read teh last byte
        newlocation = location + 4 + 8 + dsize #plus the header bytes
        return newlocation

    def getPacketBufferFromLog(self):
        return self.packetbuffer


class PyPacketBuffer():
    def __init__(self):
        self.databuffer = []
        self.tsbuffer = []
        self.length = 0

    def addtolist(self, pypkt, ts):
        self.databuffer.append(pypkt)
        self.tsbuffer.append(ts)
        self.length += 1

    def getFromList(self,index):
        if index < self.length:
            pkt = self.databuffer[index]
            ts = self.databuffer[index]
            return pkt, ts
        else:
            # out of bounds
            return None, None

    def getLengthOfBuffer(self):
        return self.length
