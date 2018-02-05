#python template
#imports
import json
import protobuf


#example type might be "Comm"
class Type_Python_Reader(Threading.thread):
	def __init__(): #whatever is needed here
	
	
	def run():
		#initialize ports and stuff
		
		while not shutdown_event.is_set():
			#receive from the host
			data, addr = sock.read(0.1)
			
			if data: #did we get anything?
				self.packet_buffer.push(data)
				
				#find good packet
				n = 0
				while self.packet_buffer.len() > IRISS_Packet.UAPACKET.MIN_PACKET_SIZE:
					#get message out of the buffer
					msg = self.packet_buffer.popPacket()
					
					if msg:
						msg.displ()
						
						#log the packet
						self.packet_log.writePacket(msg)
						
						#get message type id, however we don't use it yet
						topic = msg.getDataType()
						
						#call our handlers
						if topic in ProcessTopics:
							ProcessTopics[topic](msg)
							#This should be changed 
						else:
							print 'Unhandled Message [%i]' % topic
					else:
						self.packet_buffer.pop()
						n = n + 1
				if n > 0:
					self.logger.warning('dropped = %i',n)
		#----
		# after while loop
		
		#close socket
		sock.close()
		
		#run forever
		while not shutdown_event.is_set():
			socks = dict(poller.poll(100))
			if telem_sock in socks and socks[telem_sock] == zmq.POLLIN:
			
				#get a message
				topic, msg = telem_sock.recv_multipart()
				
				#convert binary to int literal
				topic = int(topic, 2)
		
		print('\tTelemetryTask [closed]')

	def buildJson(msg):
		#Take relevant information from the msg packet and convert to JSON
		
	def 
