import sqlite3
import time
import threading
import node

DB_FILENAME = "sense_data.sqlite"
SENSE_DATA_CREATE = "create table if not exists SenseData (Source TEXT, TimeStamp INTEGER, SenseName TEXT, SenseVal REAL)"
SENSE_DATA_INSERT = "insert into SenseData values (?, ?, ?, ?)"

def init_database():
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(SENSE_DATA_CREATE)
		db.commit()
	except Exception as e:
		db.rollback()
	finally:
		db.close()
		_lock.release()
		
def insert_sense_data(sense_name, sense_val, source=node.id, timestamp=int(time.time())):
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(SENSE_DATA_INSERT, (source, timestamp, sense_name, sense_val))
		db.commit()
	except Exception as e:
		db.rollback()
	finally:
		db.close()
		_lock.release()

def get_node_id():
	return node.id;

_lock = threading.RLock()
init_database()
