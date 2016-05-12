import json
import sense
import content
import threading
import config

class SyncPackage:
	
	def __init__(self, id = None, source = None, start_time = None, end_time = None, sense_data = [], content_data = [] ):
		self.id = id
		self.source = source
		self.start_time = start_time
		self.end_time = end_time
		self.sense_data = sense_data
		self.content_data = content_data
	
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
		
		ret.sense_data = []
		for sdat in sd:
			ret.sense_data.append(sense.SenseDatum.from_dict(sdat))
		ret.content_data = []
		
		for cdat in cd:
			ret.content_data.append(content.ContentCommand.from_dict(cdat))
		
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
