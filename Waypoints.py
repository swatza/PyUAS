

class Waypoint_Manager(object):

	def __init__(self, list_of_waypoints):
		self.list = list_of_waypoints
		self.counter = 0
	
	def nextWaypoint(self):
		incrementCounter()
		return self.list[counter]
	
	def incrementCounter(self):
		self.counter += 1
		
	def newWaypointList(self, new_list):
		self.list = new_list
		self.counter = len(new_list)
		
class Waypoint(object):
	#position (lat,lon & x,y)
	#altitude
	#number
	
	def __init__(self, position_lla, position_enu, ASL, id, radius, vertical):
		self.lat = position_lla[0]
		self.lon = position_lla[1]
		self.e = position_enu[0]
		self.n = position_enu[1]
		self.asl = ASL
		self.radius = radius
		self.id_num = id
		self.vertical_sep = vertical
		
	def checkRadius(self,current_enu):
		e = current_enu[0]
		n = current_enu[1]
		u = current_enu[2]
		u_dif = math.abs(u - self.vertical_sep)
		if u_dif < self.vertical_sep:
			r = math.sqrt(math.pow(e-self.e,2) + math.pow(n-self.n,2))
			if r <= self.radius:
				return True
			else:
				return False
		else:
			return False
		