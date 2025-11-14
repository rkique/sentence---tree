import json

# Read the JSON file
with open('tree_data.json', 'r') as file:
    data = json.load(file)

# Access the 'nodes' list and print each 'id'
for node in data['nodes']:
    id = node['id']
    if not id.startswith('Inner'):
        print(node['id'])