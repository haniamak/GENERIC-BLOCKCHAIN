import os
import time
import socket
import sctp
import keyboard
import blockList
import nodeList
import userList
import sys


def initialize_server():
    if len(sys.argv) == 3:
        dir = sys.argv[1]
        server_ip, server_port = sys.argv[2].split(':')

        print(dir, server_ip, server_port)
        os.chdir(dir)
        print(f"Working directory: {os.getcwd()}")

    else:
        print("Usage: python node.py <path_to_working_directory> <ip:port>")
        sys.exit(1)

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
    # Initialize node, user and block lists
    server_socket = initialize_server()

    node_list = nodeList.NodeList()
    node_list.fromFile("nodes/nodes.json")

    user_list = userList.UserList()
    user_list.fromFile("users/users.json")

    block_list = blockList.BlockList().load()

    print(f"Node list:\n {node_list}")
    print(f"User list:\n {user_list}")
    print(f"Block list:\n {block_list}")

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
