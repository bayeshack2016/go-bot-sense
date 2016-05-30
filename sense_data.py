import sqlite3
import time
import threading
import config
import sense

DB_FILENAME = "sense_data.sqlite"
SENSE_DATA_CREATE = "create table if not exists SenseData (Source TEXT, TimeStamp INTEGER, SenseName TEXT, SenseVal REAL)"
SENSE_DATA_INSERT = "insert into SenseData values (?, ?, ?, ?)"
SENSE_DATA_SELECT_CHUNK = "select * from SenseData where Source = ? and TimeStamp >= ? and TimeStamp < ?"

def init_database():
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(SENSE_DATA_CREATE)
		db.commit()
	except Exception as e:
		db.rollback()
		raise(e)
	finally:
		db.close()
		_lock.release()
		
def insert_sense_data(sense_name, sense_val, source=config.node.id, timestamp=int(time.time())):
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

def select_sense_data_chunk(source, start_time, end_time):
	results = None
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(SENSE_DATA_SELECT_CHUNK,(source, start_time, end_time))
		results = cursor.fetchall()
	finally:
		db.close()
		_lock.release()
	ret = []
	if results is not None:
		for result in results:
			ret.append(map_sense_datum(result))
	return ret

def map_sense_datum(result):
	return sense.SenseDatum(source=result[0], timestamp=result[1], sense_name=result[2], sense_val=result[3])

def get_node_id():
	return config.node.id;

_lock = threading.RLock()
init_database()
