#Assorted Library
import math

f = 1/298.257223563
Re = 6378137

'''
==============
MATH FUNCTIONS
==============
''' 
def unwrapAngle(angle):
	#see matlab code for this
	print angle
	out = angle;
	while (out>math.pi):
		out = out - 2*math.pi
	while (out<-math.pi):
		out = out + 2*math.pi
	return out
	
def NED2LLA(NED, center):
	#Convert from NED to LLA (assume altitude is ASL)
	N = NED[0]
	E = NED[1]
	mu0 = center[0]
	l0 = center[1]
	Rn = Re / math.sqrt(1 - (2*f - math.pow(f,2))*math.pow(math.sin(math.radians(mu0)),2))
	Rm = Rn * (1 - (2*f - math.pow(f,2)))/(1 - (2*f - math.pow(f,2))*math.pow(math.sin(math.radians(mu0)),2))
	dmu = math.atan2(1,Rm) * N
	mu = mu0 + dmu
	dl = math.atan2(1,Rn*math.cos(math.radians(mu)))*E
	l = l0 + dl
	LLA = [mu,l,-NED[2]]
	return LLA
	
	
def ENU2LLA(ENU, center):
	#Convert from ENU to LLA (assume altitude is ASL)
	N = ENU[1]
	E = ENU[0]
	mu0 = center[0]
	l0 = center[1]
	Rn = Re / math.sqrt(1 - (2*f - math.pow(f,2))*math.pow(math.sin(math.radians(mu0)),2))
	Rm = Rn * (1 - (2*f - math.pow(f,2)))/(1 - (2*f - math.pow(f,2))*math.pow(math.sin(math.radians(mu0)),2))
	dmu = math.atan2(1,Rm) * N
	mu = mu0 + dmu
	dl = math.atan2(1,Rn*math.cos(math.radians(mu)))*E
	l = l0 + dl
	LLA = [mu,l,-NED[2]]
	return LLA
	
def LLA2NED(LLA, center):
	#convert from LLA to NED (assume altitude is ASL)
	mu = LLA[0]
	l = LLA[1]
	mu0 = center[0]
	l0 = center[1]
	dmu = mu - mu0
	dl = l - l0
	Rn = Re / math.sqrt(1 - (2*f - math.pow(f,2))*math.pow(math.sin(math.radians(mu0)),2))
	Rm = Rn * (1 - (2*f - math.pow(f,2)))/(1 - (2*f - math.pow(f,2))*math.pow(math.sin(math.radians(mu0)),2))
	dN = dmu / (math.atan2(1,Rm))
	dE = dl  / (math.atan2(1,Rn*math.cos(math.radians(mu0))))
	NED = [dN, dE, -LLA[2]]
	return NED
	
def LLA2ENU(LLA, center):
	#convert from LLA to ENU (assume altitude is ASL)
	mu = LLA[0]
	l = LLA[1]
	mu0 = center[0]
	l0 = center[1]
	dmu = mu - mu0
	dl = l - l0
	Rn = Re / math.sqrt(1 - (2*f - math.pow(f,2))*math.pow(math.sin(math.radians(mu0)),2))
	Rm = Rn * (1 - (2*f - math.pow(f,2)))/(1 - (2*f - math.pow(f,2))*math.pow(math.sin(math.radians(mu0)),2))
	dN = dmu / (math.atan2(1,Rm))
	dE = dl  / (math.atan2(1,Rn*math.cos(math.radians(mu0))))
	ENU = [dE, dN, LLA[2]]
	return ENU

'''
===============
MISC FUNCTIONS
===============

def loadConfigFile(filename):
	#path stuff here
	#Read in lines, parse into dictionary
	pass
	
def loadAircraftFile(dof,name):
	filename = name + '_' + dof +'.ini'
	if dof == '6DOF':
		data = loadConfigFile(filename)
		params = parseAircraftParameters(data,'6DOF')
	elif dof == '1A':
		data = loadConfigFile(filename)
		params = parseAircraftParameters(data,'1A')
	elif dof == 'DUBINS':
		data = loadConfigFile(filename)
		params = parseAircraftParameters(data,'DUBINS')
	else:
		#Error: Unknown Type
		
	return params

def loadInitialConditionsFile():
	pass


def parseAircraftParameters(data,type):
	if type == '6DOF':
		#Do stuff
		pass
	elif type == '1A':
		#Do less stuff
		pass
	elif type == 'DUBINS':
		#Do I even do stuff?
		pass
	else:
		#Error: Type not implemented yet
		pass
	return parameters
'''
	
	
