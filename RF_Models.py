'''
Need a class to allow for easy generation of RF measurements based on terrain information and a transmitter site
'''

import math
import random
import sys
import assorted_lib
import numpy as np

LIGHT_SPEED = 3000000 #Approximate

'''
Classes for generating RF Measurements
'''
class Terrain_RF_Model(object):
	def __init__(self):
		pass
	
	def generateMeasurement(transmitterInfo, ENU_Rec):
		#get the value from SPLAT! File 
		pass
		
		
	#Returns a predicted path loss value from a SPLAT! file given a location
	def readFromSPLATFile(filename,LLA): 
		#Find a specific location from a splat file!
		numOfBytes = 4 # A float should be 4 Bytes 
		#Calculate offset (Look how we store file, where do we keep information about spacing, etc)
		offset = 4 * LLA
		#Binary; convert to float 
		#open file
		f.open(filename,'r')
		#seek to the location of value
		f.seek(offset,0)
		#read in the bytes
		value = f.read(numOfBytes)
		#close file
		f.close()
		#parse float
		predicted_pl = float(value)
		
		return predicted_pl
		

class Simple_RF_Model(object):
	
	def __init__(self,noiseType,CLLA):
		self.noise = noiseType
		self.CenterLLA = CLLA
	
	def generateMeasurement(self,transmitter_info, enu_receiver, receiver_gains):
		TransENU = assorted_lib.LLA2ENU(transmitter_info.LLA_Pos, self.CenterLLA)
		xdif = TransENU[0] - enu_receiver[0];
		ydif = TransENU[1] - enu_receiver[1];
		zdif = TransENU[2] - enu_receiver[2];
		
		distance = math.sqrt(math.pow(xdif,2) + math.pow(ydif,2) + math.pow(zdif,2))
		
		fspl = 20 * math.log10(distance) + 20*math.log10(transmitter_info.frequencyGHZ) - 147.55
		
		if self.noise == 0:
			#Use random white noise
			n = (random.random() * 10)-5 #5 to 5 dB
		elif self.noise == 1:
			#Use a log normal
			n = np.random.lognormal(0,3,1)
		else:
			n = 0;
			
		pl = fspl + n
		
		ss = transmitter_info.transmit_power + transmitter_info.antenna_gain + receiver_gains - pl
		
		return ss


	
'''
Storage class for all of the information regarding an RF transmitter
'''
class RF_Transmitter(object):
	
	#Transmit Power
	#Antenna Gain
	#Frequency
	#Location LLA 
	def __init__(self,Pt, Gt, freq, LLA):
		self.transmit_power = Pt
		self.antenna_gain = Gt
		self.frequencyGHZ = freq/1000000
		self.frequencyMHZ = freq/1000
		self.frequency = freq
		self.wavelength = LIGHT_SPEED/self.frequency
		self.LLA_Pos = LLA #Array [Lat, Lon, Altitude (ASL)]