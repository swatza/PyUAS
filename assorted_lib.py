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
	

'''
class waypoint():
	
	def __init__():
'''