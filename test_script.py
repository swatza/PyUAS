#Test Script

import integrators
import math


#Constructor with 1 second time steps
integrator = integrators.simple_integrator(1)
#initialize an initial state
x = 0
y = 0
yaw = 0
velocity = 1
state = [x,y,yaw,velocity]
inputs = [math.pi/2,0]

#loop test for 10 seconds
for index in range(0,10):
	new_state = integrator.iterateState(inputs, state)
	print 'The state is %f : %f : %f : %f' ,(new_state[0],new_state[1],new_state[2],new_state[3])
	state = new_state
	