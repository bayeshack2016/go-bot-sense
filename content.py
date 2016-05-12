import json

class ContentType:
	HTML = "text/html"
	PDF = "application/pdf"
	JSON = "application/json"
	JPG = "image/jpeg"
	PNG = "image/png"
	GIF = "image/gif"
	BIN = "application/octet-stream"
	TEXT = "text/plain"
	
class ContentMetadata:
	def __init__(self, id=None, description = None, content_type = None, content_size = None, create_date = None, publish_date = None, expire_date = None, author = None, alt_text = None, target_nodes = None, target_groups = None):
		self.id = id
		self.description = description
		self.content_type = content_type
		self.content_size = content_size
		self.create_date = create_date
		self.publish_date = publish_date
		self.expire_date = expire_date
		self.author = author
		self.alt_text = alt_text
		self.target_nodes = target_nodes
		self.target_groups = target_groups
	
	def to_string(self):
		return self.to_json()
	
	def to_json(self):
		return json.dumps( vars(self), default=lambda o: o.__dict__ )

	def __str__(self):
		return self.to_string()
	
	@staticmethod
	def from_dict(dict):
		return ContentMetadata(id=dict["id"], description=dict["description"], content_type=dict["content_type"], create_date=dict["create_date"], publish_date=dict["publish_date"], expire_date=dict["expire_date"], author=dict["author"], alt_text=dict["alt_text"], target_nodes=dict["target_nodes"], target_groups=dict["target_groups"])

class Content:
	metadata = None
	data = None
	
	def __init__(self, metadata=None, data=None):
		self.metadata = metadata
		self.data = data
	
	def __str__(self):
		return self.to_string()
		
	def to_string(self):
		return self.to_json()

	def to_json(self):
		return json.dumps( vars (self), default=lambda o: o.__dict__)

	@staticmethod
	def from_dict( dict ):
		return Content(metadata=ContentMetadata.from_dict(dict["metadata"]), data=dict["data"])
		
class ContentCommand:
	ADD = "add"
	UPDATE = "update"
	DELETE = "delete"
	
	def __init__(self, command=None, content=None, authority=None, timestamp=None):
		self.command = command
		self.content = content
		self.authority = authority
		self.timestamp = timestamp
	
	def __str__(self):
		return self.to_string()
		
	def to_string(self):
		return self.to_json()

	def to_json(self):
		return json.dumps( vars (self), default=lambda o: o.__dict__)

	@staticmethod
	def from_dict( dict ):
		return ContentCommand(command=dict["command"], authority=dict["authority"], timestamp=dict["timestamp"], content = Content.from_dict(dict["content"]))
	
	
	