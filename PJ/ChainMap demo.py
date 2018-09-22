from collections import ChainMap

mem = ChainMap() # mem = {}

mem['x'] = 5
mem['y'] = 7

mem = mem.new_child()

mem['x'] = 2

print(mem['x'], mem['y'])

mem = mem.parents

print(mem['x'], mem['y'])

mem = mem.parents

print(mem)
