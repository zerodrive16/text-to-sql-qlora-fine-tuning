import json 

with open('train_spider.json') as f: 
    data = json.load(f)

print(f"Number of entries: {len(data)}")
print("\n")
print(f"Keys per entry: {list(data[0].keys())}")
print("\n")
print(f"Example entry: {data[0]}")
print("\n")
print(f"Example SQL query: {data[0]['query']}")