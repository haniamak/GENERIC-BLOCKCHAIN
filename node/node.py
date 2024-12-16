import os
import time
import socket
# import sctp
import blockList
import nodeList
import userList
import sys
import random
import atexit

server_ip = ""
server_port = ""
running = True


def send_data(node, entry_id, author_id, file_path):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.connect((node.ip, int(node.port)))
        print(f"Connected to {node.ip}:{node.port}")
    except Exception as e:
        print(f"Failed while connecting to {node.ip}:{node.port}: {e}")
        return False

    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False

        with open(file_path, "rb") as file:
            file_data = file.read()

        msg = f"FILE:{len(file_data)}:{entry_id}:{author_id}:" 
        full_message = msg.encode() + file_data 

        print(f"Sending file with message to {node.ip}:{node.port}")
        server_socket.send(full_message)

    except Exception as e:
        print(f"Error during file transmission: {e}")
        return False
    finally:
        server_socket.close()
        return True

def receive_file(data, addr):
    try:
        
        # Ensure we've received data properly
        if not data:
            print(f"No data received from {addr}")
            return
        
        message = data.decode()
        if message.startswith("FILE:"):
            
            # Extract the metadata from the header
            _, file_size, entry_id, author_id = message.split(":")[:4]
            

            file_size = int(file_size)
            print(f"Receiving file with Entry ID: {entry_id}, Author ID: {author_id}, File size: {file_size} bytes from {addr}")

            # Get the actual file data (everything after the header)
            file_data = data[len(data) - file_size:]  # Extract the file data (after the header)

            # Ensure the file data size matches the expected size
            if len(file_data) != file_size:
                print(f"Warning: Expected file size {file_size}, but received {len(file_data)} bytes.")
            
            # Save the file with a meaningful name
            file_name = f"received_{entry_id}_{author_id}.dat"
            with open(file_name, "wb") as file:
                file.write(file_data)
            print(f"File {file_name} received and saved successfully")

            # Log receipt
            with open("received_files_log.txt", "a") as log:
                
                log.write(f"Received file: {file_name}, Entry ID: {entry_id}, Author ID: {author_id}, From: {addr}\n")
                log.flush()

            

    except Exception as e:
        print(f"Error during file reception: {e}")




def initialize_server():
    global server_ip, server_port
    if len(sys.argv) == 3:
        dir = sys.argv[1]
        server_ip, server_port = sys.argv[2].split(':')

        print(dir, server_ip, server_port)
        os.chdir(dir)
        print(f"Working directory: {os.getcwd()}")

    else:
        print("Usage: python node.py <path_to_working_directory> <ip:port>")
        sys.exit(1)


def send_signal_to_neighbors(server_socket, node_list, signal):
    for node in node_list.nodes:
        print(f"Sending {signal} to {node.ip}:{node.port}")
        msg = signal
        server_socket.sendto(msg.encode(), (node.ip, int(node.port)))


def initiate_input():
    if not os.path.isdir("input"):
        os.mkdir("input")


def check_input():
    if len(os.listdir("input")) == 0:
        print("No files in input directory")
        return False
    return True


def send_input(node_list):

    for file in os.listdir("input"):
        print(f"File input: {file}")

        for node in node_list.nodes:
            print(f"Sending {file} to {node.ip}:{node.port}")
            send_data(node, "autor", "test", f"input/{file}")
        os.remove(f"input/{file}")


def listen():
    try:
        server_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((server_ip, int(server_port)))
        server_socket.listen(1)
        server_socket.settimeout(random.randint(3, 5))

        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")

        data = conn.recv(1024)
        print(f"Received data from {addr}: {data}")
        # message = data.decode()
        # if message.startswith("FILE:"):
        #     receive_file(conn, message, addr)
        if data.startswith(b"FILE:"):
            receive_file(data, addr)

    except Exception as e:
        print(f"No data received: {e}")


def ping(server_socket, node):
    print(f"Pinging {node.ip}:{node.port}")

    # send ping to node
    # wait for response
    # return True if response received, False otherwise
    current_time = time.time()
    msg = "ping + " + str(current_time)
    server_socket.sendto(msg.encode(), (node.ip, int(node.port)))

    try:
        data, addr = server_socket.sctp_recv(1024)
        if addr[0] != node.ip or addr[1] != int(node.port):
            print(f"Received data from unknown address: {addr}")
        if data.decode()[:4] != "pong":
            print(f"Received unexpected data: {data}")
        print(f"Received data: {data}")
        return True
    except:
        print("No data received")
        return False


def on_exit():
    # do cleanup
    print("Exiting program")


def main():
    global server_ip, server_port, running

    atexit.register(on_exit)

    # Initialize node, user and block lists
    initialize_server()

    node_list = nodeList.NodeList()
    node_list.from_file("nodes/nodes.json")

    user_list = userList.UserList()
    user_list.from_file("users/users.json")

    block_list = blockList.BlockList().load()

    print(f"Node list:\n {node_list}")
    print(f"User list:\n {user_list}")
    print(f"Block list:\n {block_list}")

    # connect_to_nodes(server_socket, node_list)

    print("Configuration finished")
    print("Starting loop, send SIGINT to stop (Ctrl+C)")
   # send_signal_to_neighbors(server_socket, node_list, "START")

    initiate_input()

    sampling_time = 2
    last_time = time.time()

    try:
        while running:
            current_time = time.time()
            if current_time - last_time >= sampling_time:
                listen()

                # try to connect to all nodes
                # connect_to_nodes(server_socket, node_list)

                # Check if we have any files in the input directory
                if check_input():
                    send_input(node_list)

                last_time = current_time
            # if keyboard.is_pressed('esc'):
            #     print("Esc pressed. Exiting loop.")
            #    # send_signal_to_neighbors(server_socket, node_list, "STOP")
            #     break
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Program finished")


if __name__ == "__main__":
    main()
