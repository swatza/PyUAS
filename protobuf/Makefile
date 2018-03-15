
all: PyPackets_pb2.py

clean:
	rm PyPackets_pb2.py

PyPackets_pb2.py: PyPackets.proto
	protoc --python_out=. PyPackets.proto

