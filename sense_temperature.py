import sense
import json
import collections
import Adafruit_ADS1x15

class ConversionCurve:
	def __init__(self, filename="temperature_curve.json", curve_points=None):
		self.curve_points = curve_points
		if curve_points is None:
			self.load_curve(filename)
	
	def load_curve(self, filename):
		raw_points = {}
		with open(filename) as data_file:
			jsondata = json.load(data_file)
			for data in jsondata:
				raw_points[data['V']] = data['T']
		self.curve_points =  collections.OrderedDict(sorted(raw_points.items(), key=lambda t: t[0]))
		
	def convert(self, adcval):
		first = True
		lastval = -1
		lasttemp = -1
		for val, temp in self.curve_points.items():
			if (lastval < 0):
				if (adcval < val):
					raise ValueError('Sensor value too small')
			else:
				if (adcval < val):
					return lasttemp + ((adcval-lastval)/(val - lastval)) * (temp - lasttemp)
			lastval = val
			lasttemp = temp
		raise ValueError('Sensor value too large')

class TemperatureSense(sense.Sense):
	def __init__(self, curve_filename=None, i2c_address=None, adc_channel=0):
		self.curve_filename = curve_filename
		self.curve = None
		self.i2c_address = i2c_address
		self.adc = None
		self.adc_channel = adc_channel
		self.adc_gain = 1.0
	
	def get_value(self):
		volts = self.adc.read_adc(self.adc_channel, gain=self.adc_gain)
		return self.curve.convert(volts)
	
	def init(self,config):
		if self.i2c_address is None:
			if len(config) > 0:
				self.i2c_address = config[0]
		if self.curve_filename is None:
			if len(config) > 1:
				self.curve_filename = config[1]
		self.curve = ConversionCurve(filename=self.curve_filename)
		self.adc = Adafruit_ADS1x15.ADS1115(address=self.i2c_address)
		
	def stop(self):
		pass
		