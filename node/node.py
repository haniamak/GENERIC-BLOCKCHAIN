import blockList
import nodeList
import userList
import time
from pynput import keyboard

# np. blockList.initBlockList() # initialize blockList

# initialize nodeList
nL = nodeList.NodeList()

# add nodes to nodeList
nL.addNode('100.200.300.400', '1234')
nL.addNode('200.300.400.500', '2345')

# save nodeList to file
fileName = 'nodes/nodes.json'
nL.toFile(fileName)

# load nodeList from file
rNL = nodeList.NodeList()
rNL.fromFile(fileName)

# print nodeList
print(rNL)

# create users to node
ul = userList.UserList()
u1 = userList.User(user_id=4, key="klucz222")
u2 = userList.User(user_id=5, key="klucz444")

# add users
ul.addUser(u1)
ul.addUser(u2)

# save to file
file_path = "users/users.json"
ul.toFile(file_path)

# read from file
rUL = userList.UserList()
rUL.fromFile(file_path)

rUL.showUsers()

# handling blocks
block1 = blockList.Block("Block 1")
block2 = blockList.Block("Block 2", prev_block=block1)
block1.next_block = block2

block2.save()

print(block1.read())

last_time = time.time()
continue_loop = True

def on_press(key):
  try:
    print(f'Alphanumeric key {key.char} pressed')
  except AttributeError:
    print(f'Special key {key} pressed')

def on_release(key):
  global continue_loop
  if key == keyboard.Key.esc:
    print("Esc pressed. Exiting...")
    continue_loop = False
    return False

def main_loop():
  global last_time
  while continue_loop:
    current_time = time.time()
    if current_time - last_time >= 10:
      print("Waiting...")
      last_time = current_time

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

main_loop()

listener.join() 

print("Continuing with the program")