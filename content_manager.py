import content
import content_data
import time

def list():
	return content_data.select_all_metadata()

def get_metadata(content_id):
	return content_data.select_metadata(content_id)
	
def get_content(content_id):
	return content_data.select_content(content_id)

def store(id, description, content_type, data, publish_date = None, expire_date = None, author = None, alt_text = None, target_nodes = None, target_groups = None):
	create_date = int(time.time())
	metadata = content.ContentMetadata()
	metadata.id = id
	metadata.description = description
	metadata.content_type = content_type
	metadata.content_size = len(data)
	metadata.create_date = create_date
	metadata.publish_date = publish_date
	metadata.expire_date = expire_date
	metadata.author = author
	metadata.alt_text = alt_text
	metadata.target_nodes = target_nodes
	metadata.target_groups = target_groups
	
	content_data.insert_content(metadata, data)

def update(old_id, metadata, data):
	create_date = int(time.time())
	metadata.create_date = create_date
	content_data.update_content(old_id, metadata, data)

def update_from_vals(old_id, new_id, description, content_type, data, publish_date = None, expire_date = None, author = None, alt_text = None, target_nodes = None, target_groups = None):
	metadata = content.ContentMetadata()
	metadata.id = new_id
	metadata.description = description
	metadata.content_type = content_type
	metadata.content_size = len(data)
	metadata.publish_date = publish_date
	metadata.expire_date = expire_date
	metadata.author = author
	metadata.alt_text = alt_text
	metadata.target_nodes = target_nodes
	metadata.target_groups = target_groups
	
	update(old_id, metadata, data)

def delete(content_id):
	content_data.delete_content(content_id)

