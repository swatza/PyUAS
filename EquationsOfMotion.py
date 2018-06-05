import math
import numpy as np
import assorted_lib

#Super Class 
class VehicleModels(object):
	pass
	
	def iterateState(self):
		pass

#Sub Class
class SixDoFModel(VehicleModels):

	def __init__(self):
		pass
		#parse an aircraft parameter file

	def calculateForces(self,state):
	
		Va 
		beta
		alpha
	
		CL = self.CL0 + self.CLalpha * alpha + self.CLq * self.c/2/Va * q + self.CLde * de
		CD = self.CDmin + self.K * math.pow((CL - self.CLmin),2)
		CY = self.CY0 + self.CYbeta * beta + self.CYp * self.b/2/Va * p + self.CYr * self.b/2/Va * r + self.CYda * da + self.CYdr * dr
		
		L = .5 * density * math.pow(Va,2) * ap.S * CL
		D = .5 * density * math.pow(Va,2) * ap.S * CD
		C = .5 * density * math.pow(Va,2) * ap.S * CY
		
		X = math.cos(alpha) * -D + -math.sin(alpha) * -L
		Y = C
		Z = math.sin(alpha) * -D + math.cos(alpha) * -L
		
		forces = [X,Y,Z]
		return 
		
	def calculateMoments(self,state):
	
		Cm = ap.Cm0 + ap.CMalpha * alpha + ap.Cmq * ap.c/2/Va * q + ap.Cmde * de
		Cl = ap.Cl0 + ap.Clbeta * beta + ap.Clp * ap.b/2/Va * p + ap.Clr * ap.b/2/Va * r + ap.Clda * da + ap.Cldr * dr
		Cn = ap.Cn0 + ap.Cnbeta * beta + ap.Cnp * ap.b/2/Va * p + ap.Cnr * ap.b/2/Va * r + ap.Cnda * da + ap.Cndr * dr
		
		m = .5 * density * math.pow(Va,2) * ap.S * ap.c * Cm
		l = .5 * density * math.pow(Va,2) * ap.S * ap.b * Cl
		n = .5 * density * math.pow(Va,2) * ap.S * ap.b * Cn
		
		moments = [l,m,n]
		return moments

	def calculateDerivatives(self,state,Forces,Moments):
		#Variables
		g = 9.81 #assume constant
		m = self.vehicle_mass #assume constant for now
		
		Ixx = self.Ixx
		Ixy = self.Ixy
		Ixz = self.Ixz
		Iyy = self.Iyy
		Izz = self.Izz
		Iyz = self.Iyz
		
		L = Moments[0]
		M = Moments[1]
		N = Moments[2]
		
		X = Forces[0]
		Y = Forces[1]
		Z = Forces[2]
		
		u = state[3]
		v = state[4]
		w = state[5]
		
		P = state[6]
		Q = state[7]
		R = state[8]
		
		if self.type == 'Quat':
			q0 = state[9]
			q1 = state[10]
			q2 = state[11]
			q3 = state[12]
			#Convert to get the roll-pitch-yaw angles
			euler = quat2euler([q0,q1,q2,q3])
			Theta = euler[0]
			Phi = euler[1]
			Psi = euler[2]
		else:
			#if we are using them as states
			Theta = state[9]
			Phi = state[10]
			Psi = state[11]
		
		p = P; #This is true for a flat earth apprx. which holds for velocities less than mach 3
		q = Q;
		r = R;
		
		#Linear Accelerations body frame
		udot = R*v - Q*w - g*math.sin(Theta) + 1/m*X;           #u-acceleration [ft/s^2]
		vdot = P*w - R*u + g*math.cos(Theta)*math.sin(Phi) + 1/m*Y;  #v-acceleration [ft/s^2]
		wdot = Q*u - P*v + g*math.cos(Theta)*math.cos(Phi) + 1/m*Z;  #w-acceleration [ft/s^2]
		
		#Velocities in the Earth Frame
		xdot =  u*math.cos(Theta)*math.cos(Psi) + v*(math.sin(Phi)*math.sin(Theta)*math.cos(Psi)-math.cos(Phi)*math.sin(Psi)) + w*(math.cos(Phi)*math.sin(Theta)*math.cos(Psi)+math.sin(Phi)*math.sin(Psi)); #x-velocity [ft/s]
		ydot =  u*math.sin(Psi)*math.cos(Theta) + v*(math.sin(Phi)*math.sin(Theta)*math.sin(Psi)+math.cos(Phi)*math.cos(Psi)) + w*(math.cos(Phi)*math.sin(Theta)*math.sin(Psi)-math.sin(Phi)*math.cos(Psi)); #y-velocity [ft/s]
		zdot =  u*math.sin(Theta) - v*(math.sin(Phi)*math.cos(Theta)) - w*(math.cos(Phi)*math.cos(Theta)); #z-velocity [ft/s]
		
		#Angular Accelerations
		Pdot = (Ixz*(N+Q*Hx) - Izz*L + Ixz^2*R*q + Izz^2*R*q + Ixx*Ixz*P*q - Ixz*Iyy*Q*p + Ixz*Izz*P*q - Iyy*Izz*Q*r)/(Ixz^2 - Ixx*Izz); #Body Roll Angular acceleration [rad/s^2]
		Qdot = (M + Ixz*P*p - Ixx*P*r + Izz*R*p - Ixz*R*r - R*Hx)/Iyy; #Body Pitch Angular acceleration [rad/s^2]
		Rdot =  -(Ixx*(N+Q*Hx) - Ixz*L + Ixx^2*P*q + Ixz^2*P*q - Ixx*Iyy*Q*p + Ixx*Ixz*R*q - Ixz*Iyy*Q*r + Ixz*Izz*R*q)/(Ixz^2 - Ixx*Izz); #Body Yaw Angular acceleration [rad/s^2]
		
		if self.type == 'Quat':
			#Quaternion Kinematic DEQs 
			q0dot = 0.5*(-P*q1-Q*q2-R*q3);
			q1dot = 0.5*(P*q0+R*q2-Q*q3);
			q2dot = 0.5*(Q*q0-R*q1+P*q3);
			q3dot = 0.5*(R*q0+Q*q1-P*q2);
			
			Xdot = [Pdot,Qdot,Rdot,udot,vdot,wdot,xdot,ydot,zdot,q0dot,q1dot,q2dot,q3dot]
		else:
			#Euler Kinematic DEQs
			Phidot   = P + Q*sin(Phi)*tan(Theta) + R*cos(Phi)*tan(Theta);   #Euler Roll Angular Velocity [rad/s]
			Thetadot = Q*cos(Phi) - R*sin(Phi);                             #Euler Pitch Angular Velocity [rad/s] 
			Psidot   = Q*sin(Phi)*sec(Theta) + R*cos(Phi)*sec(Theta);       #Euler Yaw Angular Velocity [rad/s]
			
			Xdot = [Pdot,Qdot,Rdot,udot,vdot,wdot,xdot,ydot,zdot,Phidot,Thetadot,Psidot]
			
		return Xdot
	#End calculateDerivatives
	
	def takeStepRK4(self,state,dT):
		#first step
		Forces = self.calculateForces(state)
		Moments = self.calculateMoments(state)
		k1_state = self.calculateDerivatives(state,Forces,Moments)
		
		#second step
		state2 =  np.array(state) + np.array(k1_state) * dT/2
		Forces = calculateForces(state2)
		Moments = calculateMoments(state2)
		k2_state = self.calculateDerivatives(state2,Forces,Moments) 
		
		#third step
		state3 =  np.array(state) + np.array(k2_state) * dT/2
		Forces = self.calculateForces(state3)
		Moments = self.calculateMoments(state3)
		k3_state = self.calculateDerivatives(state3,Forces,Moments) 
		
		#Fourth step
		state4 =  np.array(state) + np.array(k3_state) * dT
		Forces = self.calculateForces(state4)
		Moments = self.calculateMoments(state4)
		k4_state = self.calculateDerivatives(state4,Forces,Moments) 
		
		#Add the steps together
		state_out = np.array(state) + dT/6 * (np.array(k1) + 2*np.array(k2) + 2*np.array(k3) + np.array(k4))
		return state_out
		

class OneAKinematicsEoM(object):

	def __init__(self):
		self.wind_east = 0
		self.wind_north = 0
		#load the default model parameters (Ttwistor)
		self.bchi_dot = 0.5
		self.bchi = 0.1
		self.ah_dot = 1.0
		self.bh_dot = 0.011
		self.bh = 0.00115
		self.bVa = 0.01
		

	def calculateDerivatives(self, state, inputs):
		#yaw = states[3] #if gamma_a = 0
		wn = self.wind_north
		we = self.wind_east
		
		chidot = state[2]
		chi = state[3]
		hdot = state[4]
		h = state[5]
		Va = state[6]
		
		Va_C = inputs[0]
		h_C = inputs[4]
		hdot_C = inputs[3]
		chi_C = inputs[2]
		chidot_C = inputs[1]
		
		yaw = chi - math.asin(1/Va * (wn*-math.sin(chi)+we*math.cos(chi))) #Wind relative calculation
	
		pn_dot = Va*math.cos(yaw) + wn
		pe_dot = Va*math.sin(yaw) + we
		delta_chi = chi_C - chi
		delta_chi = assorted_lib.unwrapAngle(delta_chi)
		if (chidot_C != 0):
			if (chi_C == 0):
				chidot_dot = self.bchi_dot * (chidot_C - chidot)
			else:
				chidot_dot = self.bchi_dot * (chidot_C - chidot) + self.bchi * delta_chi
		else:
			chidot_dot = self.bchi_dot * (chidot_C - chidot) + self.bchi * delta_chi
		hdot_dot = -self.ah_dot * hdot_C - self.bh_dot * hdot + self.bh*(h_C - h)
		Va_dot = self.bVa * (Va_C - Va)
		
		state_dot = [pn_dot,pe_dot,chidot_dot,chidot,hdot_dot,hdot,Va_dot]
		return state_dot
	
	def integrateState(self,state,state_dot,dT):		
		pn = state[0] + state_dot[0]*dT
		pe = state[1] + state_dot[1]*dT
		chidot = state[2] + state_dot[2]*dT
		chi = state[3] + state_dot[3]*dT
		hdot = state[4] + state_dot[4]*dT
		h = state[5] + state_dot[5]*dT
		Va = state[6] + state_dot[6]*dT
		
		chi = assorted_lib.unwrapAngle(chi)
		
		new_states = [pn, pe, chidot, chi, hdot, h, Va]
		return new_states


class DubinsCarEoM(object):
	
	def integrateState(self,state,state_dot,dT):
		x = math.cos(state[2])*state[3]*dT + state[0]
		y = math.sin(state[2])*state[3]*dT + state[1]
		yaw = inputs[0]*dT + state[2]
		velocity = inputs[1]*dT + state[3]
		
		yaw = assorted_lib.unwrapAngle(yaw)
		
		new_states = [x,y,yaw,velocity]
		
		return new_states