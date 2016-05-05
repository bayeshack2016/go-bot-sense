import content
import sqlite3
import time
import threading

DB_FILENAME = "content_data.sqlite"
CONTENT_METADATA_CREATE = "create table if not exists ContentMetadata (Id TEXT PRIMARY KEY, Description TEXT, ContentType TEXT, ContentSize INTEGER, CreateDate INTEGER, PublishDate INTEGER, ExpireDate INTEGER, Author TEXT, AltText TEXT, TargetNodes TEXT, TargetGroups TEXT)"
CONTENT_DATA_CREATE = "create table if not exists ContentData (Id TEXT PRIMARY KEY, Content BLOB)"
CONTENT_METADATA_INSERT = "insert into ContentMetadata values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
CONTENT_DATA_INSERT = "insert into ContentData values (?, ?)"
CONTENT_METADATA_LIST_ALL = "select * from ContentMetadata"
CONTENT_METADATA_SELECT_BY_ID = "select * from ContentMetadata where Id = ?"
CONTENT_DATA_SELECT_BY_ID = "select Content from ContentData where Id = ?"
CONTENT_METADATA_UPDATE = "update ContentMetadata set Id=?, Description=?, ContentType=?, ContentSize=?, CreateDate=?, PublishDate=?, ExpireDate=?, Author=?, AltText=?, TargetNodes=?, TargetGroups=? where Id=?"
CONTENT_DATA_UPDATE = "update ContentData set Id=?, Content=? where Id=?"
CONTENT_METADATA_DELETE = "delete from ContentMetadata where Id=?"
CONTENT_DATA_DELETE = "delete from ContentData where Id=?"

def init_database():
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(CONTENT_METADATA_CREATE)
		cursor.execute(CONTENT_DATA_CREATE)
		db.commit()
	except Exception as e:
		db.rollback()
	finally:
		db.close()
		_lock.release()
		
def insert_content(metadata, data):
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(CONTENT_METADATA_INSERT, (metadata.id, metadata.description, metadata.content_type, metadata.content_size, metadata.create_date, metadata.publish_date, metadata.expire_date, metadata.author, metadata.alt_text, metadata.target_nodes, metadata.target_groups))
		cursor.execute(CONTENT_DATA_INSERT, (metadata.id, data))
		db.commit()
	except Exception as e:
		db.rollback()
		raise(e)
	finally:
		db.close()
		_lock.release()

def select_all_metadata():
	results = None
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(CONTENT_METADATA_LIST_ALL)
		results = cursor.fetchall()
	finally:
		db.close()
		_lock.release()
	ret = []
	if results is not None:
		for result in results:
			ret.append(map_metadata(result))
	return ret

def select_metadata(id):
	metadata = None
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(CONTENT_METADATA_SELECT_BY_ID, (id,))
		metadata = cursor.fetchone()
		if metadata is None:
			raise Exception("Content not found")
	finally:
		db.close()
		_lock.release()
	return map_metadata(metadata)
	
def select_content(id):
	metadata = None
	dat = None
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(CONTENT_METADATA_SELECT_BY_ID, (id,))
		metadata = cursor.fetchone()
		if metadata is None:
			raise Exception("Content not found")
		cursor.execute(CONTENT_DATA_SELECT_BY_ID, (id,))
		datrow = cursor.fetchone()
		if datrow is None:
			raise Exception("Content not found")
		dat = datrow[0]
	finally:
		db.close()
		_lock.release()
	ret = content.Content()
	ret.metadata = map_metadata(metadata)
	ret.data = dat
	return ret

def update_content(old_id, metadata, data):
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(CONTENT_METADATA_UPDATE, (metadata.id, metadata.description, metadata.content_type, metadata.content_size, metadata.create_date, metadata.publish_date, metadata.expire_date, metadata.author, metadata.alt_text, metadata.target_nodes, metadata.target_groups, old_id))
		cursor.execute(CONTENT_DATA_UPDATE, (metadata.id, data, old_id))
		db.commit()
	except Exception as e:
		db.rollback()
		raise(e)
	finally:
		db.close()
		_lock.release()

def delete_content(id):
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(CONTENT_DATA_DELETE, (id,))
		cursor.execute(CONTENT_METADATA_DELETE, (id,))
		db.commit()
	except Exception as e:
		db.rollback()
		raise(e)
	finally:
		db.close()
		_lock.release()

def map_metadata(result):
	ret = content.ContentMetadata()
	ret.id = result[0]
	ret.description = result[1]
	ret.content_type = result[2]
	ret.content_size = result[3]
	ret.create_date = result[4]
	ret.publish_date = result[5]
	ret.expire_date = result[6]
	ret.author = result[7]
	ret.alt_text = result[8]
	ret.target_nodes = result[9]
	ret.target_groups = result[10]
	return ret
	
_lock = threading.RLock()
init_database()
