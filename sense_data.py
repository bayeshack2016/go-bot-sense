import sqlite3
import time
import threading

SENSE_DATA_CREATE = "create table if not exists SenseData (TimeStamp INTEGER, SensorName TEXT, SensorVal REAL)"
SENSE_DATA_INSERT = "insert into SenseData values (?, ?, ?)"

def init_database():
	try:
		_lock.acquire()
		db = sqlite3.connect('sense_data.sqlite')
		cursor = db.cursor()
		cursor.execute(SENSE_DATA_CREATE)
		db.commit()
	except Exception as e:
		db.rollback()
	finally:
		db.close()
		_lock.release()
		
def insert_sense_data(sense_name, sense_val):
	timestamp = int(time.time())
	try:
		_lock.acquire()
		db = sqlite3.connect('sense_data.sqlite')
		cursor = db.cursor()
		cursor.execute(SENSE_DATA_INSERT, (timestamp, sense_name, sense_val))
		db.commit()
	except Exception as e:
		db.rollback()
	finally:
		db.close()
		_lock.release()
		
_lock = threading.RLock()
init_database()
