# Main interface to the GO Bot Sense sensors

from abc import ABCMeta, abstractmethod
from random import randint
import json
import threading
import time
import schedule
import sense_data
import config

# Requires a json configuration file called "sense.json" to define the available senses and related configuration

_senses = None

def main():
	init()

	while 1:
		schedule.run_pending()
		time.sleep(1)

def init():
	global _senses
	_senses = {}
	for conf in config.senses.values():
		sense_class = class_from_string(conf.impl_name)
		print("Sense config class -> "+str(sense_class))
		sense = sense_class()
		sense.init(conf.impl_config)
		_senses[conf.name] = sense
		print("Added sense: "+conf.name)
		schedule_sense(conf.name, sense, conf.interval)

def collect_data(sense_name, sense):
	val = sense.get_value()
	print("Sense data collected"+json.dumps( { 'sense_name': sense_name, 'value': val } ))
	sense_data.insert_sense_data(sense_name, val)

def schedule_sense(sense_name, sense, interval):
	args = (sense_name, sense)
	kw = {
		"func": collect_data,
		"parm": args,
	}
	schedule.every(interval).seconds.do(run_threaded, **kw)

def run_threaded(func, parm):
	threading.Thread(target=func, args=parm).start()

def class_from_string(name):
	components = name.split('.')
	mod = __import__(components[0])
	for comp in components[1:]:
		mod = getattr(mod, comp)
	return mod

def get( name ):
	global _senses
	#if (_senses is None):
	#	init()
	return _senses[name]

def stop():
	global _senses
	for key, val in _senses.items():
		val.stop()
	_senses = None
	
class SenseDatum:
	def __init__(self, source=None, timestamp=None, sense_name=None, sense_val=None):
		self.source = source
		self.timestamp = timestamp
		self.sense_name = sense_name
		self.sense_val = sense_val
		
	def __str__(self):
		return self.to_string()

	def to_string(self):
		return self.to_json()
	
	def to_json(self):
		return json.dumps( vars(self), default=lambda o: o.__dict__ )
	
	@staticmethod
	def from_dict( dict ):
		return SenseDatum(source=dict['source'], timestamp=dict['timestamp'], sense_name=dict['sense_name'], sense_val=dict['sense_val'])

class Sense(metaclass=ABCMeta):
	@abstractmethod
	def get_value(self):
		pass
	
	@abstractmethod
	def init(self,config):
		pass
		
	@abstractmethod
	def stop(self):
		pass
	
class FakeSense(Sense):
	def get_value(self):
		return randint(0,99)
		
	def init(self,config):
		print("FakeSense Config:")
		for x in config:
			print(x)
	
	def stop(self):
		print("FakeSense stop called")
		
if __name__ == "__main__":
	main()

