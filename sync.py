import json
import sense
import content
import threading
import config
import time
import datetime
import sense_data
import content_data
import sync_thread
import os

LAST_SYNC_FILENAME = "sync_last.dat"

_sync_thread = None

def main():
	init()
	
	while True:
		time.sleep(10)

def init():
	global _sync_thread
	try:
		get_last_sync_time()
	except FileNotFoundError as fnfe:
		set_last_sync_time(0)
	except:
		raise	
	
	#init_schedule()
	SyncNetwork.init()
	ensure_data_dir()
	
	_sync_thread = sync_thread.SyncThread()
	_sync_thread.start()
	
def stop():
	sync._sync_thread.set_stopflag()

def ensure_data_dir():
	if not os.path.isdir(config.sync.data_dir):
		os.makedirs(config.sync.data_dir)
	
def get_package_id(node_id, start_time, end_time):
	return "{0}_{1:0>10}_{2:0>10}".format(node_id, start_time, end_time)

def get_package_filename(pkg_id):
	return "{0}/{1}.syncpkg".format(config.sync.data_dir, pkg_id)

def get_last_sync_time():
	with open(LAST_SYNC_FILENAME) as data_file:
		contents = data_file.read()
	return int(contents)

def set_last_sync_time(last_sync_time):
	with open(LAST_SYNC_FILENAME, "w") as data_file:
		data_file.write(str(last_sync_time))

def load_sync_package(pkg_id):
	raw = load_sync_package_raw(pkg_id)
	json = raw.decode('utf-8')
	return SyncPackage.from_json(json)
	
def load_sync_package_raw(pkg_id):
	data = None
	with open(get_package_filename(pkg_id), "rb") as data_file:
		data = data_file.read()
	return data
	
class SyncPackage:
	
	def __init__(self, id = None, source = None, start_time = None, end_time = None, sense_data = [], content_data = [], ack_data = [], status_data = [] ):
		self.id = id
		self.source = source
		self.start_time = start_time
		self.end_time = end_time
		self.sense_data = sense_data
		self.content_data = content_data
		self.ack_data = ack_data
		self.status_data = status_data
	
	def to_json(self):		
		return json.dumps( vars(self), default=lambda o: o.__dict__ )
	
	@staticmethod
	def from_json(jsonstr):
		jsondata = json.loads(jsonstr)
		ret = SyncPackage()
		ret.id = jsondata["id"]
		ret.source = jsondata["source"]
		ret.start_time = jsondata["start_time"]
		ret.end_time = jsondata["end_time"]
		sd = jsondata["sense_data"]
		cd = jsondata["content_data"]
		al = jsondata["ack_data"]
		sl = jsondata["status_data"]
		
		#ret.sense_data = []
		for sdat in sd:
			ret.sense_data.append(sense.SenseDatum.from_dict(sdat))
		#ret.content_data = []		
		for cdat in cd:
			ret.content_data.append(content.ContentCommand.from_dict(cdat))
		#ret.ack = []
		for adat in al:
			ret.ack.append(SyncPackageAck.from_dict(adat))
		#ret.status = []
		for stat in sl:
			ret.status.append(SyncPackageStatus.from_dict(stat))
		
		return ret
	
	def to_string(self):
		return self.to_json()
	
	def __str__(self):
		return self.to_string()
		
	def to_file(self, filename):
		with open(filename, "w") as text_file:
			text_file.write(self.to_json())
	
	@staticmethod
	def from_file( filename):
		jsonstr = None
		with open(filename, "r") as text_file:
			jsonstr = text_file.read()
			#print(jsonstr)
		return SyncPackage.from_json(jsonstr)

class SyncPackageManifest:
	def __init__(self, id = None, source = None, start_time = None, end_time = None, status = None ):
		self.id = id
		self.source = source
		self.start_time = start_time
		self.end_time = end_time
		self.status = status
	
	def to_json(self):		
		return json.dumps( vars(self), default=lambda o: o.__dict__ )
	
	def to_string(self):
		return self.to_json()
	
	def __str__(self):
		return self.to_string()

class SyncPackageAck:

	def __init__(self, id, sender_id, recip_id, timestamp=int(time.time()), success = True):
		self.id = id
		self.sender_id = sender_id
		self.recip_id = recip_id
		self.timestamp = timestamp
		self.success = success
	
	def to_json(self):		
		return json.dumps( vars(self), default=lambda o: o.__dict__ )
		
	def to_string(self):
		return self.to_json()
	
	def __str__(self):
		return self.to_string()
		
	@staticmethod
	def from_dict(dict):
		return SyncPackageAck(dict["id"], dict["sender_id"], dict["recip_id"], timestamp=dict["timestamp"])
		
class SyncPackageStatus:
	
	COMPLETED = "completed"
	DELETED = "deleted"
	ACTIVE = "active"
	PENDING = "pending"
	ERROR = "error"
	
	def __init__(self, id, status, sender_id, timestamp=int(time.time())):
		self.id = id
		self.status = status
		self.sender_id = sender_id
		self.timestamp = timestamp
	
	def to_json(self):		
		return json.dumps( vars(self), default=lambda o: o.__dict__ )
		
	def to_string(self):
		return self.to_json()
	
	def __str__(self):
		return self.to_string()
		
	@staticmethod
	def from_dict(dict):
		return SyncPackageStatus(dict["id"], dict["status"], dict["sender_id"], timestamp=dict["timestamp"])

class SyncNetwork:
	_node_config_dict = {}
	_node_info_dict = {}
	_init_flag = False
	
	@staticmethod
	def init():
		if SyncNetwork._init_flag:
			return
		for sync_node in config.sync.network:
			SyncNetwork._node_config_dict[sync_node.id] = sync_node
			SyncNetwork._node_info_dict[sync_node.id] = None
		SyncNetwork._init_flag = True
	
	@staticmethod
	def get_config(node_id):
		return SyncNetwork._node_config_dict[node_id]
		
	@staticmethod
	def node_info_loaded(node_id):
		return SyncNetwork._node_info_dict[node_id] is not None
		
	@staticmethod
	def get_info(node_id):
		return SyncNetwork._node_info_dict[node_id]
	
	@staticmethod
	def set_info(node_id, node_info):
		SyncNetwork._node_info_dict[node_id] = node_info
			
if __name__ == "__main__":
	main()

