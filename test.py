import sense
import content_manager
import time
import content
import content_manager

temp = sense.get("temperature").get_value()
print('Temperature Sensor Value: {0}'.format(temp))

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
con = content_manager.get_content('TEST_CONTENT_ID')
print(str(con))
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
