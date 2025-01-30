import os
import socket
import blockList
import nodeList
import userList
import sys
import atexit
from network import *
from helpers import *

LISTEN_TIMEOUT = 1
SEND_TIMEOUT = 2

server_ip = ""
server_port = ""
running = True
limit_of_entries = 3
temporary_dir = False
listen_socket = None


def initialize_server():
    global server_ip, server_port, temporary_dir, listen_socket

    if len(sys.argv) >= 3:
        dir = sys.argv[1]
        server_ip, server_port = sys.argv[2].split(':')

        print_and_log(f"{dir}, {server_ip}, {server_port}.")
        os.chdir(dir)
        print_and_log(f"Working directory: {os.getcwd()}.")

        if len(sys.argv) == 4 and sys.argv[3] == "--temporary":
            temporary_dir = True

    else:
        print_and_log("Usage: python node.py <path_to_working_directory> <ip:port>.")
        sys.exit(1)

    listen_socket = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((server_ip, int(server_port)))
    listen_socket.listen(5)
    listen_socket.settimeout(1)

    # Create directories for everything
    if not os.path.isdir("blocks"):
        os.mkdir("blocks")
    if not os.path.isdir("entries"):
        os.mkdir("entries")
    if not os.path.isdir("nodes"):
        os.mkdir("nodes")
    if not os.path.isdir("users"):
        os.mkdir("users")
    if not os.path.isdir("input"):
        os.mkdir("input")

    # Remove logs from previous usage
    file_path = "log.txt"
    if os.path.exists(file_path):
        os.remove(file_path)
        print_and_log("Removed logs from previous usage.")


def listen(node_list, block_list):
    global listen_socket

    conn = None
    while running:
        try:
            conn, addr = listen_socket.accept()
            data = conn.recv(1024)
            if data[:4] == b"PING":
                conn.send(b"pong")
                node_list.set_online(addr[0], addr[1], True)
                print_and_log(f"Sent pong to {addr[0]}:{addr[1]}")
            elif data.startswith(b"ENTRY:") or data.startswith(b"BLOCK:"):
                datacopy = data[:]
                receive_file(datacopy, addr, block_list)
            else:
                print_and_log(f"Received unknown message: {data}")
        except socket.timeout:
            break
        except Exception as e:
            print_and_log(f"Error during connection handling: {e}")
        finally:
            if conn:
                conn.close()


def on_exit():
    # Do cleanup
    global running
    running = False
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

    block_list = blockList.BlockList()
    block_list.from_file()

    start_settigs = f'''
        Node list: {node_list}
        User list: {user_list}
        {block_list}
        '''

    print_and_log(start_settigs)
    print_and_log("Configuration finished")
    print_and_log("Starting loop, send SIGINT to stop (Ctrl+C)")

    for node in node_list:
        node_list.set_online(node.ip, node.port, False)

    try:
        while running:
            # TODO Rework, listen ma pauzować pętle
            listen(node_list, block_list)
            fake_ping(node_list)

            # Check if we have any files in the input directory
            if check_input():
                print_and_log( "New file in input folder.")
                send_input(node_list)

            # Check if we have enough entries to create a block
            if len(os.listdir("entries")) >= limit_of_entries:
                print_and_log("Limit of entries reached.")
                new_block = create_block(block_list, save=not temporary_dir)
                send_latest_block_to_neighbors(node_list, new_block)

    except Exception as e:
        print_and_log(f"An error occurred: {e}")

    finally:
        if not temporary_dir:
            print_and_log("Saving data")
            block_list.save()
            node_list.to_file("nodes/nodes.json")
            user_list.to_file("users/users.json")

        log_text = f'''
Block Tree:
{block_list.tree.pretty_print()}
Entries list:
{os.listdir("entries")}
Node list:
{node_list}
User list:
{user_list}

Program finished
        '''

        print_and_log(log_text)


if __name__ == "__main__":
    main()
