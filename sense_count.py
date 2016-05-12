import sense
import threading
import RPi.GPIO as gpio

#GPIO.wait_for_edge(21, GPIO.RISING)
#GPIO.wait_for_edge(21, GPIO.FALLING)

class CountSense(sense.Sense):
	def __init__(self, pin_number=None, data_filename=None):
		self.pin_number = pin_number
		self.data_filename = data_filename
		self.current_count = 0
		self.monitor_thread = None
		self.stopping = False
	
	def get_value(self):
		return self.current_count
	
	def init(self,config):
		if self.pin_number is None:
			if len(config) > 0:
				self.pin_number = config[0]
		if self.data_filename is None:
			if len(config) > 1:
				self.data_filename = config[1]
		try:
			self.load_data_file()
		except FileNotFoundError as fnfe:
			self.current_count = 0
		except:
			raise	
			
		gpio.setmode(gpio.BCM)
		gpio.setup(self.pin_number, gpio.IN)
		
		self.monitor_thread = CountMonitorThread(self)
		self.monitor_thread.start()
		
	def load_data_file(self):
		with open(self.data_filename) as data_file:
			contents = data_file.read()
			self.current_count = int(contents)
	
	def write_data_file(self):
		with open(self.data_filename, "w") as data_file:
			data_file.write(str(self.current_count))
			
	def stop(self):
		self.stopping = True
		
class CountMonitorThread(threading.Thread):
	def __init__(self, sen):
		threading.Thread.__init__(self)
		self.sense = sen
		print(str(sen))
	
	def run(self):
		while 1:
			gpio.wait_for_edge(self.sense.pin_number, gpio.RISING)
			self.sense.current_count += 1
			self.sense.write_data_file()
			if self.sense.stopping:
				return
		