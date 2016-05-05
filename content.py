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
	id = None
	description = None
	content_type = None
	content_size = None
	create_date = None
	publish_date = None
	expire_date = None
	author = None
	alt_text = None
	target_nodes = None
	target_groups = None
	
	def to_string(self):
		return json.dumps( { 'id': self.id, 'description': self.description, 'content_type': self.content_type, 'content_size': self.content_size, 'create_date':self.create_date, 'publish_date':self.publish_date, 'expire_date':self.expire_date, 'author':self.author, 'alt_text':self.alt_text, 'target_nodes':self.target_nodes, 'target_groups':self.target_groups } )

	def __str__(self):
		return self.to_string()


class Content:
	metadata = None
	data = None
	
	def __str__(self):
		return self.to_string()

	def to_string(self):
		return self.metadata.to_string() + "|" + str(self.data)

