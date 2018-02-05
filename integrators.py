import math
import assorted_lib

class simple_integrator():
	''' Simple Dubins' Integrator '''
	#states: x, y, yaw, velocity
	#inputs: yaw rate, acceleration
	
	def __init__(self, timeStep):
		self.dT = timeStep

	def iterateState(self, inputs, states):
		dT = self.dT
		x = math.cos(states[2])*states[3]*dT + states[0]
		y = math.sin(states[2])*states[3]*dT + states[1]
		yaw = inputs[0]*dT + states[2]
		velocity = inputs[1]*dT + states[3]
		
		yaw = assorted_lib.unwrapAngle(yaw)
		
		new_states = [x,y,yaw,velocity]
		
		return new_states
		
class simple_1A_integrator_from_commanded_course():
	''' Simple integrator from SUAS Book '''
	#States: pn, pe chidot, chi, hdot, h, Va
	#Inputs: Va_C,h_C,hdot_C ,chi_C, chidot_C
	#Parameters: Wn, We, bchi_dot, bchi, bh_dot, bh, bVa
	
	def __init__(self, timeStep, parameters):
		dT = timeStep
		self.wind_north = parameters[0]
		self.wind_east = parameters[1]
		self.bchi_dot = parameters[2]
		self.bchi = parameters[3]
		self.bh_dot = parameters[4]
		self.bh = parameters[5]
		self.bVa = parameters[6]
	
	def calculateDerivatives(self, inputs, states):
		#yaw = states[3] #if gamma_a = 0
		wn = self.wind_north
		we = self.wind_east
		
		chidot = states[2]
		chi = states[3]
		hdot = states[4]
		h = states[5]
		Va = states[6]
		
		Va_C = inputs[0]
		h_C = inputs[1]
		hdot_C = inputs[2]
		chi_C = inputs[3]
		chidot_C = inputs[4]
		
		yaw = chi - math.asin(1/Va * (wn*-sin(chi)+we*cos(chi)))
	
		pn_dot = Va*math.cos(yaw) + wn
		pe_dot = Va*math.sin(yaw) + we
		chidot_dot = self.bchi_dot*(chidot_C - chidot) + self.bchi*(chi_C - chi)
		hdot_dot = self.bh_dot*(hdot_C - hdot) + self.bh*(h_C - h)
		Va_dot = self.bVa * (Va_C - Va)
		
		state_dot = [pn_dot,pe_dot,chidot_dot,hdot_dot,Va_dot]
		return state_dot
	
	def iterateState(state_dot, state):
		pn_dot = state_dot[0]
		pe_dot = state_dot[1]
		chidot_dot = state_dot[2]
		hdot_dot = state_dot[3]
		Va_dot = state_dot[4]
		
		pn = state[0] + pn_dot*dT
		pe = state[1] + pe_dot*dT
		chidot = state[2] + chidot_dot*dT
		chi = state[2]*dT + state[3]
		hdot = state[4] + hdot_dot*dT
		h = state[4]*dT + state[5]
		Va = state[6] + Va_dot*dT
		
		chi = assorted_lib.unwrapAngle(chi)
		
		new_states = [pn, pe, chidot, chi, hdot, h, Va]
		return new_states
		
	
	
