import os
import time
import socket
import sctp
import keyboard
import blockList
import nodeList
import userList

def send_data(server_socket, node, entry_id, author_id, data_list):
    total_entries = len(data_list)
    header = f"DATA:{total_entries}"
    print(f"Sending data header to {node.ip}:{node.port}: {header}")
    server_socket.sendto(header.encode(), (node.ip, int(node.port)))

    for data in data_list:
        packet = data.encode()
        server_socket.sendto(packet, (node.ip, int(node.port)))
        print(f"Sent data packet: {data}")

    print(f"All {total_entries} entries sent to {node.ip}:{node.port}")


def receive_data(server_socket, node):
    data, addr = server_socket.recvfrom(1024)
    message = data.decode()

    if message.startswith("DATA:"):
        _, total_entries = message.split(":")
        total_entries = int(total_entries)
        print(f"Receiving {total_entries} entries from {addr}")

        for _ in range(total_entries):
            chunk, _ = server_socket.recvfrom(1024)
            data_str = chunk.decode()
            print(f"Received data chunk: {data_str}")

        print(f"All entries successfully received and added to {node.entries}")


def set_working_directory():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

def initialize_server():
    server_ip = input("Input IP port (default = 127.0.0.1): ") or '127.0.0.1'
    server_port = input("Input server port (default = 10001): ") or '10001'

    server_socket = sctp.sctpsocket_tcp(socket.AF_INET)
    server_socket.bind((server_ip, int(server_port)))

    print(f"Server started at {server_ip}:{server_port}")
    return server_socket

def send_signal_to_neighbors(server_socket, node_list, signal):
    for node in node_list.nodes:
        print(f"Sending {signal} to {node.ip}:{node.port}")
        msg = signal
        server_socket.sendto(msg.encode(), (node.ip, int(node.port)))

def connect_to_nodes(server_socket, nodes):
    for node in nodes:
        print(f"Connecting to {node.ip}:{node.port}")
        try:
            server_socket.connect((node.ip, int(node.port)))
            print(f"Connected to {node.ip}:{node.port}")
        except Exception as e:
            print(f"Failed while connecting to {node.ip}:{node.port}: {e}")


def ping(server_socket, node):
    print(f"Pinging {node.ip}:{node.port}")

    # send ping to node
    # wait for response
    # return True if response received, False otherwise
    current_time = time.time()
    msg = "ping + " + str(current_time)
    server_socket.sendto(msg.encode(), (node.ip, int(node.port)))
    
    try:
        data, addr = server_socket.recvfrom(1024)
        if addr[0] != node.ip or addr[1] != int(node.port):
            print(f"Received data from unknown address: {addr}")
        if data.decode()[:4] != "pong":
            print(f"Received unexpected data: {data}")
        print(f"Received data: {data}")
        return True
    except:
        print("No data received")
        return False


def main():
    set_working_directory()

    # Initialize node, user and block lists
    node_list = nodeList.NodeList()
    node_list.fromFile("nodes/nodes.json")

    user_list = userList.UserList()
    user_list.fromFile("users/users.json")

    block_list = blockList.BlockList().load()

    print(f"Node list:\n {node_list}")
    print(f"User list:\n {user_list}")
    print(f"Block list:\n {block_list}")

    server_socket = initialize_server()

    connect_to_nodes(server_socket, node_list.nodes)

    print("Configuration finished")
    print("Starting loop, press ESC to exit")
    send_signal_to_neighbors(server_socket, node_list, "START")

    sampling_time = 2
    last_time = time.time()
    
    try:
        while True:
            current_time = time.time()
            if current_time - last_time >= sampling_time:
                # Check if we received any data
                try:
                    data, addr = server_socket.recvfrom(1024)
                    print(f"Received data from {addr}: {data}")
                except Exception as e:
                    print(f"No data received: {e}")

                last_time = current_time
            if keyboard.is_pressed('esc'):
                print("Esc pressed. Exiting loop.")
                send_signal_to_neighbors(server_socket, node_list, "STOP")
                break
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Program finished")

if __name__ == "__main__":
    main()
