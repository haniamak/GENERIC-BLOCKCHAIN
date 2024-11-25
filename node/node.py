import blockList
import nodeList
import userList
import time
import keyboard
import socket
import sctp

# np. blockList.initBlockList() # initialize blockList

# initialize nodeList
nL = nodeList.NodeList()

# add nodes to nodeList
nL.addNode('127.0.0.1', '10002', True)
nL.addNode('127.0.0.1', '10003', False)

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

server_ip = ''
server_port = ''

print("input server IP (default = 127.0.0.1):")
server_ip = input()
if server_ip == '':
    server_ip = '127.0.0.1'

print("input server port (default = 10001):")
server_port = input()
if server_port == '':
    server_port = '10001'

sk = sctp.sctpsocket_tcp(socket.AF_INET)
sk.bind((server_ip, int(server_port)))

print("Server started at " + server_ip + ":" + server_port)

for node in rNL.nodes:
    print(f"Connecting to {node.ip}:{node.port}")
    try:
        sk.connect((node.ip, int(node.port)))
        print(f"Connected to {node.ip}:{node.port}")
    except Exception as e:
        print(f"An error occurred: {e}")


print("configuration finished")
print("Starting loop, press ESC to exit")

sampling_time = 2

try:
    last_time = time.time()
    while True:
        current_time = time.time()
        if current_time - last_time >= sampling_time:
            # check if we received any data
            try:
                data, addr = sk.recvfrom(1024)
                print(f"Received data: {data}")
            except:
                print("No data received")

            last_time = current_time
        if keyboard.is_pressed('esc'):
            print("Esc pressed. Exiting loop.")
            break
except Exception as e:
    print(f"An error occurred: {e}")


print("Continuing with the program")
