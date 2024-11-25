import blockList
import nodeList
import userList
import time
import keyboard

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

try:
  last_time = time.time()
  while True:
    current_time = time.time()
    if current_time - last_time >= 10:
      print("Working...")
      last_time = current_time
    if keyboard.is_pressed('esc'):
        print("Esc pressed. Exiting loop.")
        break
except Exception as e:
    print(f"An error occurred: {e}")


print("Continuing with the program")