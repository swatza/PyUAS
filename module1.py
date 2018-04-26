import sys
import time
import json

sys.path.insert(0,'../PyUAS')
sys.path.insert(0,'../PyUAS/protobuf')
import PyPackets_pb2
from google.protobuf import json_format


#Create our demo 
msg1 = PyPackets_pb2.RF_PL_Map_Msg()
msg1.packetNum = 1
msg1.ID = "test"
msg1.time = time.time()
msg1.gp_iteration_number = 1
msg1.xGrids = 1
msg1.yGrids = 1
msg1.xSpacing = 1
msg1.ySpacing = 1
for i in range(4):
    new = msg1.cell.add()
    new.xgridNum = 10
    new.ygridNum = 15
    new.est_path_loss = 5
    new.path_loss_err = 1
    new.pred_path_loss = 2
    
msg1.centerPoint.x = 40.389
msg1.centerPoint.y = 105.39
msg1.centerPoint.z = 0
msg1.gp_learning_time = 10
msg1.gp_prediction_time = 12

msg2 = PyPackets_pb2.RF_Data_Msg()
msg2.packetNum = 1
msg2.ID = "test"
msg2.time = time.time()
msg2.lla.x = 40.1
msg2.lla.y = 100.0
msg2.lla.z = 90
msg2.attitude.x = 0
msg2.attitude.y = 0
msg2.attitude.z = 0
msg2.airspeed = 1
for i in range(3):
    new = msg2.rfNode.add()
    new.chanID = "1"
    new.rssi = 10
    new.pl_msr = 5
    new.pl_error = 0
    new.xgridNum

msg3 = PyPackets_pb2.NMStatus()
msg3.packetNum = 1
msg3.ID = "Test"
msg3.time = time.time()
msg3.numberOfMsgs = 10
msg3.avgTimeDelay = 5
msg3.totalMsgsRcv = 100
for i in range(3):
    new = msg3.subs.add()
    new.id = "sub"
    new.datatype = "AC10"
    new.port = 10000
    new.address = "192.158.10.101"
    new.msgfreq = 0.1

msg3.messagesInQue = 12
#convert each to a json string
json_string = json_format.MessageToJson(msg1)
dictOut = json.loads(json_string)
json_string = json_format.MessageToJson(msg2)
dictOut2 = json.loads(json_string)
json_string = json_format.MessageToJson(msg3)
dictOut3 = json.loads(json_string)

string = 'RF_PL_Map_Msg'
dictionaryNew = {}
dictionaryNew[string] = dictOut
dictionaryNew['Msg2'] = dictOut2
dictionaryNew['Msg3'] = dictOut3
#Merge into 1 dictionary
dictOut.update(dictOut2)
dictOut.update(dictOut3)
#output back into json
jstring = json.dumps(dictionaryNew)
#Output to text file
f = open('json_test_file.txt','w')
f.write(jstring)
f.close()
