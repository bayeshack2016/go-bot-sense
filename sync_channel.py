import json
import sync
import config
import urllib.request
import urllib.parse

from abc import ABCMeta, abstractmethod

class SyncChannels:

	_channels = {}
	_configs = {}
	_init_flag = False
	
	@staticmethod
	def init():
		if SyncChannels._init_flag:
			return
		for channel_config in config.sync.channels:
			SyncChannels._configs[channel_config.name] = channel_config
			SyncChannels._channels[channel_config.name] = None
			channel_class = SyncChannels._class_from_string(channel_config.channel_class)
			channel = channel_class()
			channel.set_name(channel_config.name)
			channel.init(channel_config.config)
			SyncChannels._channels[channel_config.name] = channel
		SyncChannels._init_flag = True
	
	@staticmethod
	def _class_from_string(name):
		components = name.split('.')
		mod = __import__(components[0])
		for comp in components[1:]:
			mod = getattr(mod, comp)
		return mod
	
	@staticmethod
	def channel(channel_name):
		return SyncChannels._channels[channel_name]
		
	@staticmethod
	def channel_config(channel_name):
		return SyncChannels._configs[channel_name]

class SyncChannel(metaclass=ABCMeta):
	@abstractmethod
	def set_name(self, name):
		pass
	
	@abstractmethod
	def get_name(self):
		pass
		
	@abstractmethod
	def init(self, config):
		pass
		
	@abstractmethod
	def open(self):
		pass
	
	@abstractmethod
	def request_info(self, home_node_id, remote_node_id):
		pass
	
	@abstractmethod
	def send_info(self, home_node_id, remote_node_id, node_config):
		pass
		
	@abstractmethod
	def request_offer(self, home_node_id, remote_node_id):
		# tell another node to make an offer
		pass
		
	@abstractmethod
	def send_offer(self, home_node_id, remote_node_id, sync_file_ids):
		# send a list of files available from a node
		pass
		
	@abstractmethod
	def request_files(self, home_node_id, remote_node_id, sync_file_ids):
		# request files from a node
		pass
		
	@abstractmethod
	def send_file(self, home_node_id, remote_node_id, sync_file_id, sync_file_data):
		# send requested file
		pass
		
	@abstractmethod
	def close(self):
		pass
	
class SharedNetworkChannel(SyncChannel):
	
	def __init__(self):
		return
	
	def set_name(self, name):
		self.name = name
	
	def get_name(self):
		return self.name
		
	def init(self, config):
		# do nothing right now
		return
	
	def open(self):
		# do nothing but in final form bring up the network adapter
		return
	
	def request_info(self, home_node_id, remote_node_id):
		values = {'node_id' : home_node_id, 'channel': self.get_name() }
		url = self._build_url(remote_node_id, '/info', values)
		req = urllib.request.Request(url, method="POST")
		response = urllib.request.urlopen(req)
		if (response.getcode() != 200):
			raise RuntimeError("Received code {}".format(response.getcode()))
	
	def send_info(self, home_node_id, remote_node_id, node_config):
		values = {'node_id' : home_node_id }
		url = self._build_url(remote_node_id, '/info', values)
		headers = {"Content-Type": "application/json"}
		data = json.dumps( vars(node_config), default=lambda o: o.__dict__ ).encode('utf-8')
		req = urllib.request.Request(url, method="PUT", headers=headers, data=data)
		response = urllib.request.urlopen(req)
		if (response.getcode() != 200):
			raise RuntimeError("Received code {}".format(response.getcode()))
			
	def request_offer(self, home_node_id, remote_node_id):
		# tell another node to make an offer		
		values = {'node_id' : home_node_id, 'channel': self.get_name() }
		url = self._build_url(remote_node_id, '/offer', values)
		req = urllib.request.Request(url, method="POST")
		response = urllib.request.urlopen(req)
		if (response.getcode() != 200):
			raise RuntimeError("Received code {}".format(response.getcode()))
		#the_page = response.read()
	
	def send_offer(self, home_node_id, remote_node_id, sync_file_ids):
		# send a list of files available from a node
		print('sync_file_ids len: '+str(len(sync_file_ids)))
		values = {'node_id' : home_node_id, 'channel': self.get_name() }
		url = self._build_url(remote_node_id, '/offer', values)
		headers = {"Content-Type": "application/json"}
		data = json.dumps(sync_file_ids).encode('utf-8')
		req = urllib.request.Request(url, method="PUT", headers=headers, data=data)
		response = urllib.request.urlopen(req)
		if (response.getcode() != 200):
			raise RuntimeError("Received code {}".format(response.getcode()))
		
	def request_files(self, home_node_id, remote_node_id, sync_file_ids):
		# request files from a node
		values = {'node_id' : home_node_id, 'channel': self.get_name() }
		url = self._build_url(remote_node_id, '/file', values)
		headers = {"Content-Type": "application/json"}
		data = json.dumps(sync_file_ids).encode('utf-8')
		req = urllib.request.Request(url, method="POST", headers=headers, data=data)
		response = urllib.request.urlopen(req)
		if (response.getcode() != 200):
			raise RuntimeError("Received code {}".format(response.getcode()))
		
	def send_file(self, home_node_id, remote_node_id, sync_file_id, sync_file_data):
		# send requested files
		values = {'node_id' : home_node_id }
		url = self._build_url(remote_node_id, '/file/{0}'.format(sync_file_id), values)
		headers = {"Content-Type": "application/json"}
		req = urllib.request.Request(url, method="PUT", headers=headers, data=sync_file_data)
		response = urllib.request.urlopen(req)
		if (response.getcode() != 200):
			raise RuntimeError("Received code {}".format(response.getcode()))
		
	def close(self):
		return
	
	#def parsed_address(node_id):
	#	address = sync.get_config(node_id).address
	#	return address.strip(":").split(":")
	
	def _build_url(self, remote_node_id, path, query_dict):
		parts = ['http://', sync.SyncNetwork.get_config(remote_node_id).address, path]
		if (query_dict is not None and len(query_dict) > 0):
			parts.append('?')
			parts.append(urllib.parse.urlencode(query_dict))
		return ''.join(parts) 