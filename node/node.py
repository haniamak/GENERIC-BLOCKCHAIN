# np. import 'blockList' from 'blockList.py'
import nodeList
import userList

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
