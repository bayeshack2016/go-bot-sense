import json
import config
import threading
import sense
import sync

def main():
	global sense_thread, sync_thread
	init()
	print("Node configuration:")
	print(str(config.node))
	
	sense_thread = threading.Thread(target = sense.main, name="sense_thread" )
	sync_thread = threading.Thread( target = sync.main, name="sync_thread" )
	
	sense_thread.start()
	print("Sense thread started")
	sync_thread.start()
	print("Sync thread started")
	
def init():
	# do nothing for the moment
	pass
	
def stop():
	# do nothing for the moment
	pass

if __name__ == "__main__":
	main()
