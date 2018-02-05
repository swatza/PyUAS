
import math
import assorted_lib

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
		
		

#Used with simple 1A kinematic model
class simple_1A_guidance_loiter():
	k_orbit = 2; #what is this?
	m = 1; #What is this?

	def __init__(self, cw):
		
		if cw:
			lambda = 1;
		else:
			lambda = 2;
			
	def circleLoiterCalc(waypoint, state):
		radius = waypoint.radius
		cn = waypoint.pn
		ce = waypoint.pe
		
		pn = state[0]
		pe = state[1]
		
		chi = state[3]
		
		psi = atan2(pe-ce,pn-cn) + 2*pi*m
		d = sqrt((pn-cn)^2 + (pe-ce)^2)
		while(psi - chi) < -pi:
			psi = psi + 2*pi
		while(psi - chi) > pi:
			psi = psi - 2*pi
		
		chi_C = psi + lambda*(pi/2 + atan2(k_orbit*(d-radius),radius))
		Va_C = Va
		h_C = waypoint.h;
		chidot_C = Va/radius;
		hdot_C = 0;
		
		inputs = [Va_C,chidot_C,chi_C,hdot_C,h_C]
		#write the return part
		return inputs