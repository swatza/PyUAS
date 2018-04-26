class Subscriber(object):
	def __init__(self, type, id, port, ip, requestFreq):
		#Provide the DataType and ID of the publisher/published message and provide your own IP, Port, and Request rate
		self.TYPE = bytearray(type) #Target Type
		self.ID = bytearray(id) #Target ID
		self.PORT = port #My PORT
		self.IP = ip #My IP
		self.FREQ = requestFreq #My Requested Data Rate
		self.lastTime = 0
		
	def getAddress(self):
		address = (self.IP,self.PORT)
		return address
		
	def printSubInfo(self):
		print self.TYPE
		print self.ID
		print self.PORT
		print self.IP
		
	def compareSub(self,id,dt,port,ip):
		if self.TYPE == dt:
			if self.ID == id:
				if self.PORT == port:
					if self.IP == ip:
						return True
		return False
		
	def getRequestTime(self):
		return 1 / self.FREQ #convert to seconds
		
	def setLastTime(self, time):
		self.lastTime = time
		
	def getLastTime(self):
		return self.lastTime