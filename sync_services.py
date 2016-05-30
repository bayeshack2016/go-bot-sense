import os
import config
import sync_channel
import sync_data
from sync import SyncNetwork, SyncPackageStatus, load_sync_package_raw, load_sync_package
from sync_channel import SyncChannels
from bottle import route, get, put, post, run, template, request, response
import urllib.request
import urllib.parse
import threading
import json

index_html = '''<h1>GO Bot Sense Node: {{ node_id }}</h1>'''

def main():
	port = int(os.environ.get('PORT', config.sync.services_port))
	run(host=config.sync.services_ip, port=port, debug=True)

@route('/')
def index():
    return template(index_html, node_id=config.node.id)

@post('/info')
def request_info():
	print("sync_services: request_info()")
	remote_node_id = request.query['node_id']
	channel = request.query['channel']
	
	threading.Thread(target=send_info, args=(channel, remote_node_id), name="Request info callback").start()
    
	response.status = 200

@put('/info')
def receive_info():
	print("sync_services: receive_info()")
	remote_node_id = request.query['node_id']
	#if remote_node_id != config.node.id:
	info_json = request.json
	info = config.NodeConfig.from_dict(info_json)
	SyncNetwork.set_info(remote_node_id, info)
	response.status = 200

@post('/offer')
def request_offer():
	print("sync_services: request_offer()")
	remote_node_id = request.query['node_id']
	channel = request.query['channel']
	
	threading.Thread(target=send_offer, args=(channel, remote_node_id), name="Request offer callback").start()
    
	response.status = 200

@put('/offer')
def receive_offer():
	print("sync_services: receive_offer()")
	remote_node_id = request.query['node_id']
	channel = request.query['channel']
	offer_list = request.json
	print("Offer received -> "+json.dumps(offer_list))
	threading.Thread(target=send_request_for_missing_files, args=(channel, remote_node_id, offer_list), name="Request missing files callback").start()
    
	response.status = 200

@post('/file')
def request_files():
	print("sync_services: request_files()")
	remote_node_id = request.query['node_id']
	channel = request.query['channel']
	id_list = request.json
	
	if len(id_list) > 0:
		threading.Thread(target=send_files, args=(channel, remote_node_id, id_list), name="Request files callback").start()
    
	response.status = 200
	
@put('/file/<id>')
def receive_file(id):
	print("sync_services: receive_info()")
	remote_node_id = request.query['node_id']
	if (sync_data.package_exists(id)):
		print("Received duplicate file. Skipping.")
	else:
		data = request.body.read()
		with open(get_package_filename(pkg_id), "wb") as data_file:
			data_file.write(data)
		pkg = load_sync_package(id)
		sync_data.insert_package(pkg, SyncPackageStatus.PENDING)
	
def send_info(channel, remote_node_id):
	print("sync_services: send_info()")
	SyncChannels.channel(channel).send_info(config.node.id, remote_node_id, config.node)

def send_offer(channel, remote_node_id):
	print("sync_services: send_offer()")
	sync_file_ids = sync_data.select_package_ids_by_status(SyncPackageStatus.ACTIVE)
	# would be better to exclude files already sent from this but need to add an entity in the db to track files sent
	SyncChannels.channel(channel).send_offer(config.node.id, remote_node_id, sync_file_ids)

def send_files(channel, remote_node_id, package_id_list):
	print("sync_services: send_files()")
	for package_id in package_id_list:
		send_file(channel, remote_node_id, package_id)

def send_file(channel, remote_node_id, package_id):
	data = load_sync_package_raw(package_id)
	SyncChannels.channel(channel).send_file(config.node.id, remote_node_id, package_id, data)

def send_request_for_missing_files(channel, remote_node_id, offer_list):
	print("sync_services: send_request_for_missing_files()")
	missing = sync_data.select_missing_packages(offer_list)
	if len(missing) > 0:
		SyncChannels.channel(channel).request_files(config.node.id, remote_node_id, missing)
	
#class FollowUpTaskRunner:
#	pass
	
if __name__ == '__main__':
	main()