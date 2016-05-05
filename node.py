import json

id = None
name = None
group = None
lat = None
long = None
elevation = None

def main():
	global id, name, group, lat, long, elev
	init()
	print("Node configuration"+json.dumps( { 'id': id, 'name': name, 'group': group, 'lat': lat, 'long':long, 'elevation':elevation } ))
	
def init():
	load_config()

# Requires a json configuration file called "node.json" to define the sense node's ID and metadata
def load_config():
	global id, name, group, lat, long, elev
	with open('node.json') as data_file:
		jsondata = json.load(data_file)
		id = jsondata["id"]
		name = jsondata["name"]
		group = jsondata["group"]
		lat = jsondata["lat"]
		long = jsondata["long"]
		elevation = jsondata["elevation"]

if __name__ == "__main__":
	main()
