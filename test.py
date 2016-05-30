import sense
import content_manager
import time
import sync
import content
import content_manager
import sync_data
import node
import config
import threading
import sync_services
import sync_channel

node_id = config.node.id
print('Node Id: {0}', node_id)

sense.init()
temp = sense.get("temperature").get_value()
print('Temperature Sensor Value: '+str(temp))
count = sense.get("count").get_value()
print('Count Sensor Value: '+str(count))
sense.stop()

print('Inserting content')
content_data = "A quick brown fox jumped over the lazy dog"
content_id = 'TEST_CONTENT_ID'
content_description = 'Just some test content'
content_type = content.ContentType.TEXT
content_manager.store(content_id, content_description, content_type, content_data)
print('...done')

print("Listing content")
list = content_manager.list()
print('\n'.join(map(str, list)))
print('...done')

print("Loading metadata")
metadata = content_manager.get_metadata('TEST_CONTENT_ID')
print(str(metadata))
print('...done')

print("Loading content")
cont = content_manager.get_content('TEST_CONTENT_ID')
print(str(cont))
print('...done')

print("Updating content")
content_data = "A quick brown fox jumped over the updated dog"
content_id = 'TEST_CONTENT_ID'
content_description = 'Just some updated test content'
con = content_manager.update_from_vals('TEST_CONTENT_ID', content_id, content_description, content_type, content_data)
print('...done')

print("Deleting content")
content_manager.delete('TEST_CONTENT_ID')
print('...done')

print("Save and load of sync package")
sense_data = []
content_data = []
sense_data.append(sense.SenseDatum(source=node_id, sense_name='temperature', sense_val=25))

content_command = content.ContentCommand(command=content.ContentCommand.ADD, authority="respectmy", content = cont)
content_data.append(content_command)

pkg = sync.SyncPackage()
pkg.id = "TESTSYNCPKG1"
pkg.source = node_id
pkg.start_time = 1000000
pkg.end_time = 1000100
pkg.sense_data = sense_data
pkg.content_data = content_data

pkg.to_file('testpkg.json')

pkgin = sync.SyncPackage.from_file('testpkg.json')
print(str(pkgin))
print('...done')

print("Inserting package")
sync_data.insert_package(pkg, sync.SyncPackageStatus.ACTIVE)
print('...done')

print("Selecting active packages")
packages = sync_data.select_packages_by_status(sync.SyncPackageStatus.ACTIVE)
print('...done')

print("Updating package")
sync_data.update_package_status(pkg.id, sync.SyncPackageStatus.COMPLETED)
print('...done')

print("Deleting package")
sync_data.delete_package(pkg.id)
print('...done')

print("Inserting ack")
sync_data.insert_ack(pkg.id, True, pkg.source, pkg.source)
print('...done')

print("Selecting ack chunk")
start_date = int(time.time())
end_date = start_date + 60
start_date = start_date - (15 * 60)
acks = sync_data.select_ack_chunk(pkg.source, start_date, end_date)
print('...done')

print("Deleting ack")
sync_data.delete_ack(pkg.id, pkg.source)
print('...done')

pkg_id = sync.get_package_id(pkg.source, pkg.start_time, pkg.end_time)
print("Generated package ID => {0}".format(pkg_id))

pkg_filename = sync.get_package_filename(pkg_id)
print("Generated package filename => {0}".format(pkg_filename))


sync.SyncNetwork.init()
sync_channel.SyncChannels.init()

# start up the sync services
threading.Thread(target=sync_services.main).start()

# sleep a little to give the server time to start
time.sleep(10)

channel = sync_channel.SyncChannels.channel('shared')
channel.request_info(config.node.id, config.node.id)

time.sleep(2)
info = sync.SyncNetwork.get_info(config.node.id)
print("Info: "+str(info))

channel.request_offer(config.node.id, config.node.id)

