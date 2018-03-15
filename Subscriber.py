class Subscriber(object):
	def __init__(self, type, id, port, ip):
		self.TYPE = bytearray(type)
		self.ID = bytearray(id)
		self.PORT = port
		self.IP = ip
		
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