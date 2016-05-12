import sense
import content_manager
import time
import sync
import content
import content_manager
import node
import config

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
