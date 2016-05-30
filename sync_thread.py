import sync
import sync_data
import sense
import sense_data
import content
import content_data
import datetime
import time
import config
import threading

class SyncThread(threading.Thread):
	

	def __init__(self):
		threading.Thread.__init__(self)
		self._hourly_schedule = None
		self._stopped = False
		self.init_schedule()
		
	def run(self):
		while 1:			
			now = int(time.time())
			next = self.next_run_time()
			# kludge to handle the fact that next could be in the past in certain edge cases
			delay = next - now
			if delay > 0:
				time.sleep(delay)
			
				if self._stopped:
					return
				
				self.write_sync_package()
				self.sync_files()
	
	def write_sync_package(self):
		print("Starting package write")
		last_sync_time = sync.get_last_sync_time()
		new_sync_time = int(time.time())
		sense_dat = sense_data.select_sense_data_chunk(config.node.id, last_sync_time, new_sync_time)
		#temporary until content stuff gets fixed
		content_dat = []
		ack_dat = sync_data.select_ack_chunk(config.node.id, last_sync_time, new_sync_time)
		status_dat = []
		pkg_id = sync.get_package_id(config.node.id, last_sync_time, new_sync_time)
		pkg = sync.SyncPackage(id = pkg_id, source = config.node.id, start_time = last_sync_time, end_time = new_sync_time, sense_data = sense_dat, content_data = content_dat, ack_data = ack_dat, status_data = status_dat)
		filename = sync.get_package_filename(pkg_id)
		pkg.to_file(filename)
		sync_data.insert_package(pkg, sync.SyncPackageStatus.ACTIVE)
		sync.set_last_sync_time(new_sync_time)
		print("Successfully wrote package {0}".format(pkg_id))
		
	def sync_files(self):
		pass
	
	def set_stopflag(self):
		self._stopped = True
	
	def init_schedule(self):
		self._hourly_schedule = []
		min = config.sync.start_min
		while min < 60:
			self._hourly_schedule.append(min)
			min += config.sync.period_min		

	def next_run_time(self):
		now = datetime.datetime.now()
		next_min = None
		next_hour = now.hour
		for smin in self._hourly_schedule:
			if smin > now.minute:
				next_min = smin
				break
		if next_min is None:
			next_min = self._hourly_schedule[0]
			next_hour = (next_hour+1)%24	
		
		# this needs fixed. It will cause a crash at midnight otherwise. Either check for rollover in day, month, and year or use some timedelta approach.
		next = datetime.datetime(now.year, now.month, now.day, hour = next_hour, minute = next_min)
		return next.timestamp()
