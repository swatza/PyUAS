
import math
import assorted_lib
import Waypoints

'''
class simple_guidance_alg():
	Kp_heading = .65
	
	def __init__(self, parameters):
		#do something
		
	def calculateControl(waypoint,state)
		xdif = (waypoint.pn - state[0])
		ydif = (waypoint.pe - state[1])
		
		heading_req = math.atan2(ydif,xdif)
		heading_error = heading_req - state[2]
		heading_error = assorted_lib.unwrapAngle(heading_error)
		turn_rate = self.Kp_heading*heading_error
'''
		
#Used with simple 1A kinematic model
class Simple_1A_Guidance():
	def __init__(self, cw):
		cw = False
		if cw:
			self.Lambda = 1;
		else:
			self.Lambda = -1;
			
	def circleLoiterCalc(self, waypoint, state):
		k_orbit = 2; #what is this for?
		m = 1; #What is this?
		radius = waypoint.radius
		cn = waypoint.n
		ce = waypoint.e
		
		pn = state[0]
		pe = state[1]
		pi = math.pi
		chi = state[3]
		Va = state[6]
		
		#psi = math.atan2(pn-cn,pe-ce)
		psi = math.atan2(pe-ce,pn-cn) + 2*pi*m
		d = math.sqrt(math.pow((pn-cn),2) + math.pow((pe-ce),2))
		psi = assorted_lib.unwrapAngle(psi-chi)
		
		chi_C = psi + self.Lambda*(pi/2 + math.atan2(k_orbit*(d-radius),radius))
		Va_C = Va
		h_C = waypoint.asl;
		chidot_C = Va/radius * self.Lambda;
		hdot_C = 0;
		
		inputs = [Va_C,chidot_C,chi_C,hdot_C,h_C]
		#write the return part
		return inputs
		
	def followTrajectory(self):
		pass