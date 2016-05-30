import sqlite3
import sync
import threading
import time

DB_FILENAME = "sync_data.sqlite"

CREATE_SYNC_PACKAGE = "CREATE TABLE IF NOT EXISTS sync_package (id TEXT PRIMARY KEY, source TEXT, start_time INTEGER, end_time INTEGER, status TEXT)"
INSERT_SYNC_PACKAGE = "INSERT INTO sync_package VALUES (?, ?, ?, ?, ?)"
UPDATE_SYNC_PACKAGE = "UPDATE sync_package SET status = ? WHERE id = ?"
SELECT_SYNC_PACKAGE_BY_STATUS = "SELECT * FROM sync_package WHERE status = ?"
SELECT_SYNC_PACKAGE_ID_BY_STATUS = "SELECT id FROM sync_package WHERE status = ?"
SELECT_SYNC_PACKAGE_ALL = "SELECT * FROM sync_package"
DELETE_SYNC_PACKAGE = "DELETE FROM sync_package WHERE id = ?"
SYNC_PACKAGE_EXISTS = "SELECT EXISTS(SELECT 1 FROM sync_package WHERE id=? LIMIT 1)"

CREATE_SYNC_ACK = "CREATE TABLE IF NOT EXISTS sync_ack (id TEXT, sender_id TEXT, recip_id TEXT, timestamp INTEGER, success TEXT, PRIMARY KEY (id, recip_id))"
INSERT_SYNC_ACK = "INSERT INTO sync_ack VALUES (?, ?, ?, ? ,?)"
SELECT_SYNC_ACK_CHUNK = "SELECT * FROM sync_ack WHERE recip_id == ? AND timestamp >= ? AND timestamp < ?"
DELETE_SYNC_ACK = "DELETE FROM sync_ack WHERE id = ? AND recip_id = ?"

def init_database():
	print('Initializing sync database')
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(CREATE_SYNC_PACKAGE)
		cursor.execute(CREATE_SYNC_ACK)
		db.commit()
	except Exception as e:
		db.rollback()
		raise(e)
	finally:
		db.close()
		_lock.release()

def insert_package(sync_pkg, status):
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(INSERT_SYNC_PACKAGE, (sync_pkg.id, sync_pkg.source, sync_pkg.start_time, sync_pkg.end_time, status))
		db.commit()
	except Exception as e:
		db.rollback()
		raise(e)
	finally:
		db.close()
		_lock.release()

def update_package_status(id, status):
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(UPDATE_SYNC_PACKAGE, (status, id))
		db.commit()
	except Exception as e:
		db.rollback()
		raise(e)
	finally:
		db.close()
		_lock.release()

def select_packages_by_status(status):
	results = None
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		if status is None:
			cursor.execute(SELECT_SYNC_PACKAGE_ALL)
		else:
			cursor.execute(SELECT_SYNC_PACKAGE_BY_STATUS, (status,))
		results = cursor.fetchall()
	finally:
		db.close()
		_lock.release()
	ret = []
	if results is not None:
		for result in results:
			ret.append(map_package(result))
	return ret

def select_package_ids_by_status(status):
	results = None
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(SELECT_SYNC_PACKAGE_ID_BY_STATUS, (status,))
		results = cursor.fetchall()
	finally:
		db.close()
		_lock.release()
	ret = []
	if results is not None:
		for result in results:
			ret.append(result[0])
	return ret

def package_exists(id):
	ret = False
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(SYNC_PACKAGE_EXISTS, (id,))
		ret = cursor.fetchone()[0] == 1
	finally:
		db.close()
		_lock.release()
	return ret

def select_missing_packages(id_list):
	# examine a list of packages and return a list of the ids for files not already synced
	ret = []
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		for id in id_list:
			cursor = db.cursor()
			cursor.execute(SYNC_PACKAGE_EXISTS, (id,))
			if cursor.fetchone()[0] == 0:
				ret.append(id)
			cursor.close()
	finally:
		db.close()
		_lock.release()
	return ret

def delete_package(id):
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(DELETE_SYNC_PACKAGE, (id,))
		db.commit()
	except Exception as e:
		db.rollback()
		raise(e)
	finally:
		db.close()
		_lock.release()

def map_package(result):
	ret = sync.SyncPackageManifest()
	ret.id = result[0]
	ret.source = result[1]
	ret.start_time = result[2]
	ret.end_time = result[3]
	ret.status = result[4]
	return ret

def insert_ack(id, success, sender_id, recip_id, timestamp=int(time.time())):
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(INSERT_SYNC_ACK, (id, sender_id, recip_id, timestamp, success))
		db.commit()
	except Exception as e:
		db.rollback()
		raise(e)
	finally:
		db.close()
		_lock.release()

def select_ack_chunk(recip_id, start_time, end_time):
	results = None
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(SELECT_SYNC_ACK_CHUNK,(recip_id, start_time, end_time))
		results = cursor.fetchall()
	finally:
		db.close()
		_lock.release()
	ret = []
	if results is not None:
		for result in results:
			ret.append(map_ack(result))
	return ret

def delete_ack(id, recip_id):
	try:
		_lock.acquire()
		db = sqlite3.connect(DB_FILENAME)
		cursor = db.cursor()
		cursor.execute(DELETE_SYNC_ACK, (id,recip_id))
		db.commit()
	except Exception as e:
		db.rollback()
		raise(e)
	finally:
		db.close()
		_lock.release()

def map_ack(result):
	return sync.SyncPackageAck(result[0], result[1], result[2], timestamp = result[3], success = result[4] )

_lock = threading.RLock()
init_database()

