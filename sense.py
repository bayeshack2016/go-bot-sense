# Main interface to the GO Bot Sense sensors

from abc import ABCMeta, abstractmethod
from random import randint
import json
import threading
import time
import schedule
import sense_data

# Requires a json configuration file called "sense.json" to define the available senses and related configuration

_senses = None
_sense_configs = {}

def main():
	init()

	while 1:
		schedule.run_pending()
		time.sleep(1)

def init():
	load_config()
	for config in _sense_configs.values():
		sense_class = class_from_string(config.impl_name)
		sense = sense_class()
		sense.init(config.impl_config)
		_senses[config.name] = sense
		schedule_sense(config.name, sense, config.interval)

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

def load_config( ):
	global _senses, _sense_configs
	with open('sense.json') as data_file:
		jsondata = json.load(data_file)
	_senses = {}
	for sense_config in jsondata:
		config = SenseConfig()
		
		config.name = sense_config["name"]
		config.interval = sense_config["interval"]
		config.impl_name = sense_config["impl_name"]
		config.impl_config = sense_config["impl_config"]
		_sense_configs[config.name] = config
	return
	
def get( name ):
	global _senses
	if (_senses is None):
		load()
	return _senses[name]
	
class SenseConfig:
	def __init__(self):
		self.name = None
		self.interval = None
		self.impl_name = None
		self.impl_config = []
	
	def to_string(self):
		return json.dumps( { 'name': self.name, 'interval': interval, 'impl_name': self.impl_name, 'impl_config': self.impl_config } )

class Sense(metaclass=ABCMeta):
	@abstractmethod
	def get_value(self):
		pass
	
	@abstractmethod
	def init(self,config):
		pass
	
class FakeSense(Sense):
	def get_value(self):
		return randint(0,99)
		
	def init(self,config):
		print("FakeSense Config:")
		for x in config:
			print(x)

if __name__ == "__main__":
	main()

