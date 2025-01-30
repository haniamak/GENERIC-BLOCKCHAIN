import os
import time
import socket
import blockList
import nodeList
import userList
import entryList
from entryList import Entry, EntryList
from blockList import Block, Tree, TreeNode
import sys
import random
import atexit
import json
import uuid
from datetime import datetime
import hashlib

LISTEN_TIMEOUT = 1
SEND_TIMEOUT = 2

server_ip = ""
server_port = ""
running = True
limit_of_entries = 3
temporary_dir = False
listen_socket = None
entries_directory = "entries/"


def send_latest_block_to_neighbors(node_list, latest_block):
    for node in node_list.nodes:
        if node.online:
            try:
                server_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                server_socket.connect((node.ip, int(node.port)))

                block_data = json.dumps(latest_block.to_dict()).encode()
                message = f"BLOCK:{len(block_data)}:".encode() + block_data

                server_socket.send(message)
                server_socket.close()
                node.send_block = False

                log_text = f"Sent block {[x.entry_id for x in latest_block.list_of_entries.entries]} to {node.ip}:{node.port}"
                print(log_text)
                new_log(log_text)

            except Exception as e:
                log_text = f"FAILED: Sent block {[x.entry_id for x in latest_block.list_of_entries.entries]} to {node.ip}:{node.port}\n {e}"
                print(log_text)
                new_log(log_text)


def send_entry(node, uuid_str, author_id, file_path):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(SEND_TIMEOUT)

    try:
        server_socket.connect((node.ip, int(node.port)))
    except Exception as e:
        log_text = f"Failed while connecting to {node.ip}:{node.port}: {e}"
        print(log_text)
        new_log(log_text)
        return False

    try:
        if not os.path.exists(file_path):
            log_text = f"File not found: {file_path}"
            print(log_text)
            new_log(log_text)
            return False

        with open(file_path, "rb") as file:
            file_data = file.read()

        entry_id = uuid_str
        msg = f"ENTRY:{len(file_data)}:{entry_id}:{author_id}:"
        full_message = msg.encode() + file_data

        log_text = f"Sending file with message to {node.ip}:{node.port}"
        print(log_text)
        new_log(log_text)

        server_socket.send(full_message)
    except socket.timeout:
        print(f"Timeout while sending file to {node.ip}:{node.port}")
        return False
    except Exception as e:
        print(f"Error during file transmission: {e}")
        return False
    finally:
        server_socket.close()
        return True


def create_block(block_list):
    list_of_entries = entryList.EntryList()
    entries_id = []
    for filename in os.listdir(entries_directory)[:limit_of_entries]:
        file_path = os.path.join(entries_directory, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
            entry = entryList.Entry(
                loaded_data["entry_id"], loaded_data["author_id"], loaded_data["data"])
            list_of_entries.add_entry(entry)
            entries_id.append(loaded_data["entry_id"])
        if os.path.exists(file_path):
            os.remove(file_path)

    block = blockList.Block(list_of_entries)
    block.prev_block = block_list.last_hash()
    block_list.add_block(block)

    log_text = f"Created block with entries: {entries_id}."
    print(log_text)
    new_log(log_text)

    if not temporary_dir:
        block_list.save()

    return block


def new_log(text):
    log_time = str(datetime.now())[:19]
    with open("log.txt", "a") as log:
        log.write(log_time + " - " + text + "\n")
        log.flush()


def receive_file(data, addr, block_list):
    try:
        # Ensure we've received data properly
        # if not data or len(data) == 0:
        #     print(f"No data received from {addr}")
        #     return

        try:
            message = data.decode()
        except Exception as e:
            log_text = f"Error decoding data from {addr}: {e}"
            print(log_text)
            new_log(log_text)
            return

        # Check the type of received message, currently only supports ENTRY and BLOCK
        if message.startswith("ENTRY:"):
            # Extract the metadata from the header
            _, file_size, entry_id, author_id = message.split(":")[:4]

            file_size = int(file_size)

            # Get the actual file data (everything after the header)
            # Extract the file data (after the header)
            file_data = data[len(data) - file_size:]

            # Ensure the file data size matches the expected size
            if len(file_data) != file_size:
                log_test = f"Warning: Expected file size {file_size}, but received {len(file_data)} bytes."
                print(log_test)
                new_log(log_test)

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
            log_text = f"Received file: {file_name}, Entry ID: " + \
                f"{entry_id}, Author ID: {author_id}, From: {addr}"
            print(log_text)
            new_log(log_text)

        elif message.startswith("BLOCK:"):
            # new_log("Received block")
            block_data = message[message.find(":", message.find(":")+1)+1:]
            # new_log(f"Block data: {block_data}")
            block_dict = json.loads(block_data)
            block = blockList.Block()
            block.from_dict(block_dict)
            if block_list.add_block(block):
                log_text = f"Received block of hash {block.hash()} child of {block.prev_block}\n"
                print(log_text)
                new_log(log_text)
            else:
                log_text = f"Received INVALID block of hash {block.hash()} child of {block.prev_block}\n"
                print(log_text)
                new_log(log_text)

        else:
            log_text = f"Received unknown message: {message}"
            print(log_text)
            new_log(log_text)

    except Exception as e:

        log_text = f"Error during file reception: {e}"
        print(log_text)
        new_log(log_text)


def initialize_server():
    global server_ip, server_port, temporary_dir, listen_socket

    if len(sys.argv) >= 3:
        dir = sys.argv[1]
        server_ip, server_port = sys.argv[2].split(':')

        print(dir, server_ip, server_port)
        os.chdir(dir)
        print(f"Working directory: {os.getcwd()}")

        if len(sys.argv) == 4 and sys.argv[3] == "--temporary":
            temporary_dir = True

    else:
        print("Usage: python node.py <path_to_working_directory> <ip:port>")
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

    # remove logs from previous usage
    file_path = "log.txt"
    if os.path.exists(file_path):
        os.remove(file_path)
        log_text = "Removed logs from previous usage"
        print(log_text)
        new_log(log_text)


def send_signal_to_neighbors(server_socket, node_list, signal):
    for node in node_list.nodes:
        log_text = f"Sending {signal} to {node.ip}:{node.port}"
        print(log_text)
        new_log(log_text)
        msg = signal
        server_socket.sendto(msg.encode(), (node.ip, int(node.port)))


def check_input():
    if len(os.listdir("input")) == 0:
        log_text = "No files in input directory"
        print(log_text)
        # new_log(log_text)
        return False
    return True


def send_input(node_list):
    files = sorted(os.listdir("input"))
    for file in files:
        log_text = f"File input: {file}"
        print(log_text)
        new_log(log_text)
        any_sent = False

        uuid_str = str(hashlib.sha256(file.encode()).hexdigest())

        for node in node_list.nodes:
            if not node.online:
                continue

            log_text = f"Sending {file} to {node.ip}:{node.port}"
            print(log_text)
            new_log(log_text)

            sent = send_entry(node, uuid_str, author_id="autor",
                              file_path=f"input/{file}")
            if sent:
                node_list.set_online(node.ip, node.port, True)
                any_sent = True

                # logging
                log_text = f"File {file} sent to {node.ip}:{node.port}"
                new_log(log_text)
            else:
                node_list.set_online(node.ip, node.port, False)

        if any_sent:
            file_data = open(f"input/{file}", "r", encoding="utf-8").read()

            entry_dict = {
                "entry_id": uuid_str,
                "author_id": "autor",
                "data": file_data
            }

            file_name = f"""entries/received_{entry_dict["entry_id"]}.json"""
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(entry_dict, f)

            os.remove(f"input/{file}")


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
                print(f"Sent pong to {addr[0]}:{addr[1]}")
            elif data.startswith(b"ENTRY:") or data.startswith(b"BLOCK:"):
                datacopy = data[:]
                receive_file(datacopy, addr, block_list)
            else:
                print(f"Received unknown message: {data}")
        except socket.timeout:
            break
        except Exception as e:
            print(f"Error during connection handling: {e}")
        finally:
            if conn:
                conn.close()


def ping(node_list):
    for node in node_list.nodes:
        if node.online:
            continue
        res = ping_node(node)
        if res:
            node_list.set_online(node.ip, node.port, True)
        else:
            node_list.set_online(node.ip, node.port, False)


def ping_node(node):
    print(f"Pinging {node.ip}:{node.port}")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.connect((node.ip, int(node.port)))
    except Exception as e:
        print(f"PING[{server_ip}:{server_port}]: Failed while connecting to " +
              f"{node.ip}: {node.port}: {e}")
        return

    # send ping to node
    # wait for response
    # return True if response received, False otherwise
    try:
        server_socket.send(b"PING")
        server_socket.settimeout(random.randint(3, 5))
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


def fake_ping(node_list):
    for node in node_list.nodes:
        if node.online:
            continue
        node_list.set_online(node.ip, node.port, True)


def on_exit():
    # Do cleanup.
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
    print(start_settigs)
    new_log(start_settigs)

    print("Configuration finished")
    print("Starting loop, send SIGINT to stop (Ctrl+C)")

    for node in node_list:
        node_list.set_online(node.ip, node.port, False)

    try:
        while running:
            # TODO Rework, listen ma pauzować pętle
            listen(node_list, block_list)
            fake_ping(node_list)

            # Check if we have any files in the input directory
            if check_input():
                log_text = "New file in input folder"
                print(log_text)
                new_log(log_text)
                send_input(node_list)

            # Check if we have enough entries to create a block
            if len(os.listdir("entries")) >= limit_of_entries:
                log_text = "Limit of entries reached"
                print(log_text)
                new_log(log_text)
                new_block = create_block(block_list)
                send_latest_block_to_neighbors(node_list, new_block)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if not temporary_dir:
            print("Saving data")
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

        print(log_text)
        new_log(log_text)

if __name__ == "__main__":
    main()
