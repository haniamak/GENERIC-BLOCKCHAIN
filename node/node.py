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
import json
import uuid

server_ip = ""
server_port = ""
running = True


def send_data(node, author_id, file_path):
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

        entry_id = uuid.uuid4()
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
            print(f"Receiving file with Entry ID: {entry_id}, Author ID: {
                  author_id}, File size: {file_size} bytes from {addr}")

            # Get the actual file data (everything after the header)
            # Extract the file data (after the header)
            file_data = data[len(data) - file_size:]

            # Ensure the file data size matches the expected size
            if len(file_data) != file_size:
                print(f"Warning: Expected file size {
                      file_size}, but received {len(file_data)} bytes.")

            file_data = file_data.decode('utf-8')

            entry_dict = {
                "entry_id": entry_id,
                "author_id": author_id,
                "data": file_data
            }

            file_name = f"entries/received_{entry_id}.json"
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(entry_dict, f)

            # Log receipt
            with open("received_files_log.txt", "a") as log:

                log.write(f"Received file: {file_name}, Entry ID: {
                          entry_id}, Author ID: {author_id}, From: {addr}\n")
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
            if not node.online:
                continue

            print(f"Sending {file} to {node.ip}:{node.port}")
            # send_data(node, "autor", "test", f"input/{file}")
            # Zastanowić się gdzie trzymać autora 
            
            sent = send_data(node, author_id="autor", file_path=f"input/{file}")
            if sent:
                node_list.set_online(node.ip, node.port, True)
                os.remove(f"input/{file}")
            else:
                node_list.set_online(node.ip, node.port, False)


def listen(node_list):
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
        if data[:4] == b"PING":
            conn.send(b"pong")
            node_list.set_online(addr[0], addr[1], True)
            print(f"Sent pong to {addr[0]}:{addr[1]}")
        # message = data.decode()
        # if message.startswith("FILE:"):
        #     receive_file(conn, message, addr)
        if data.startswith(b"FILE:"):
            receive_file(data, addr)

    except Exception as e:
        print(f"No data received: {e}")


def ping(node_list):
    for node in node_list.nodes:
        if node.online:
            continue
        res = pingNode(node)
        if res:
            node_list.set_online(node.ip, node.port, True)
        else:
            node_list.set_online(node.ip, node.port, False)


def pingNode(node):
    print(f"Pinging {node.ip}:{node.port}")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.connect((node.ip, int(node.port)))
    except Exception as e:
        print(f"PING[{server_ip}:{server_port}]: Failed while connecting to {
              node.ip}:{node.port}: {e}")
        return

    # send ping to node
    # wait for response
    # return True if response received, False otherwise
    try:
        server_socket.send(b"PING")
        server_socket.settimeout(3)
        response = server_socket.recv(1024)
        if response.decode() == "pong":
            print(f"Received pong from {node.ip}:{node.port}")
            return True
        else:
            print(f"Unexpected response: {response.decode()}")
            return False
    except socket.timeout:
        print(f"Ping to {node.ip}:{node.port} timed out")
        return False
    except Exception as e:
        print(f"Error during ping: {e}")
        return False
    finally:
        server_socket.close()


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

    for node in node_list:
        node_list.set_online(node.ip, node.port, False)

    sampling_time = 2
    last_time = time.time()

    try:
        while running:
            current_time = time.time()
            if current_time - last_time >= sampling_time:
                listen(node_list)
                # ping offline nodes
                ping(node_list)

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
