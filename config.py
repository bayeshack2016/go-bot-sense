import json
import threading

_load_lock = threading.RLock()
node = None
senses = None
sync = None

def main():
	init()
	print("Node config:")
	print(str(node))
	print("Senses config:")
	for name, sense in senses.items():
		print(str(sense))
	print("Sync config:")
	print(str(sync))
	

def init(filename="config.json"):
	load(filename)

def load(filename="config.json"):
	try:
		_load_lock.acquire()
		jsonstr = None
		with open(filename, "r") as config_file:
			jsonstr = config_file.read()
		_set_from_json(jsonstr)
	finally:
		_load_lock.release()

def _set_from_json(jsonstr):
	global node, sync, senses
	
	jsondata = json.loads(jsonstr)
	senses_list = jsondata["senses"]
	sync_dict = jsondata["sync"]
	node = NodeConfig.from_dict(jsondata["node"])
	sync = SyncConfig.from_dict(jsondata["sync"])
	senses = None
	if senses_list is not None:
		senses = {}
		for sense_dict in senses_list:
			sc = SenseConfig.from_dict(sense_dict)
			senses[sc.name] = sc
	
class NodeConfig:
	def __init__(self, id=None, name=None, group=None, lat=None, long=None, elevation=None):
		self.id = id
		self.name = name
		self.group = group
		self.lat = lat
		self.long = long
		self.elevation = elevation
	
	def __str__(self):
		return self.to_string()

	def to_string(self):
		return json.dumps( vars(self), default=lambda o: o.__dict__ )
		
	@staticmethod
	def from_dict(dict):
		if dict is None:
			return None
		return NodeConfig(id=dict['id'], name=dict['name'], group=dict['group'], lat = dict['lat'], long = dict['long'], elevation = dict['elevation'])

class SenseConfig:
	def __init__(self, name=None, interval=60, impl_name=None, impl_config=[]):
		self.name = name
		self.interval = interval
		self.impl_name = impl_name
		self.impl_config = impl_config
	
	def __str__(self):
		return self.to_string()

	def to_string(self):
		return json.dumps( vars(self), default=lambda o: o.__dict__ )
		
	@staticmethod
	def from_dict(dict):
		if dict is None:
			return None
		ret = SenseConfig(name=dict['name'], interval=dict['interval'], impl_name = dict['impl_name'], impl_config = dict['impl_config'])
		if ret.impl_config is None:
			ret.impl_config = []
		return ret
		
class SyncConfig:
	SHARED = 0x00
	AD_HOC = 0x01
	SNEAKER = 0x02
	
	def __init__(self, start_min=0, period_min=10, sync_channel=SHARED, sync_channel_config=None):
		self.start_min = start_min
		self.period_min = period_min
		self.sync_channel = sync_channel
		self.sync_channel_config = sync_channel_config
	
	def __str__(self):
		return self.to_string()

	def to_string(self):
		return json.dumps( vars(self), default=lambda o: o.__dict__ )
	
	@staticmethod
	def from_dict(dict):
		if dict is None:
			return None
		return SyncConfig(start_min=dict['start_min'], period_min=dict['period_min'], sync_channel=dict['sync_channel'], sync_channel_config=dict['sync_channel_config'])

init()

if __name__ == "__main__":
	main()

