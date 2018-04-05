#Assorted Library
import math

 
def unwrapAngle(angle):
	#see matlab code for this
	out = angle;
	while (out>math.pi):
		out = out - 2*math.pi
	while (out<-math.pi):
		out = out + 2*math.pi
	return out
	

def loadConfigFile(filename):
	#path stuff here
	#Read in lines, parse into dictionary
	
	
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


def parseAircraftParameters(data,type)
	if type == '6DOF':
		#Do stuff
	elif type == '1A':
		#Do less stuff
	elif type == 'DUBINS':
		#Do I even do stuff?
	else:
		#Error: Type not implemented yet
	return parameters
		