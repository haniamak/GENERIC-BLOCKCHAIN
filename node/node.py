import os
import time
import socket
import blockList
import nodeList
import userList
import entryList
import sys
import random
import atexit
import json
import uuid
from datetime import datetime
import textwrap

server_ip = ""
server_port = ""
running = True
limit_of_entries = 3
temporary_dir = False

def send_latest_block_to_neighbors(node_list, block_list):
    if not block_list.is_empty():
        # To można zmienić, na dowolny blok, lub listę  bloków
        latest_block = block_list[-1]
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

                    log_text = f"Sent block {[x.entry_id for x in latest_block.list_of_entries]} to {node.ip}:{node.port}"
                    print(log_text)
                    new_log(log_text)

                except Exception as e:
                    log_text = f"FAILED: Sent block {[x.entry_id for x in latest_block.list_of_entries]} to {node.ip}:{node.port}"
                    print(log_text)
                    new_log(log_text)

def send_entry(node, uuidStr, author_id, file_path):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.connect((node.ip, int(node.port)))
        # print(f"Connected to {node.ip}:{node.port}")
    except Exception as e:

        ## loging
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

        entry_id = uuidStr
        msg = f"ENTRY:{len(file_data)}:{entry_id}:{author_id}:"
        full_message = msg.encode() + file_data

        log_text = f"Sending file with message to {node.ip}:{node.port}"
        print(log_text)
        new_log(log_text)

        server_socket.send(full_message)

    except Exception as e:
        print(f"Error during file transmission: {e}")
        return False
    finally:
        server_socket.close()
        return True


def create_block(block_list):
    entries_directory = "entries/"
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
    block_list.add_block(block)


# to save block_list in block.json
# block_list.save()

    # print(f"New Block created with {entries_id} entries")

def new_log(text):
    log_time = str(datetime.now())[:19]
    with open("log.txt", "a") as log:
        log.write(log_time + " - " + text + "\n")
        log.flush()

def receive_file(data, addr, block_list):
    try:
        # Ensure we've received data properly
        if not data:
            print(f"No data received from {addr}")


            return

        message = data.decode()
        if message.startswith("ENTRY:"):
            # Extract the metadata from the header
            _, file_size, entry_id, author_id = message.split(":")[:4]

            file_size = int(file_size)
            # print(
            #     f"Receiving file with Entry ID: {entry_id}, " +
            #     f"Author ID: {author_id}, File size: {file_size} bytes from {addr}")

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
            log_text = f"Received file: {file_name}, Entry ID: " + f"{entry_id}, Author ID: {author_id}, From: {addr}\n"
            print(log_text)
            new_log(log_text)

            # Check limit of entries in one block
            # entries_directory = "entries/"
            # num_entries = len(os.listdir(entries_directory))
            # if num_entries >= limit_of_entries:
            #     create_block(block_list)
            #     send_latest_block_to_neighbors(node_list, block_list)

        elif message.startswith("BLOCK:"):
            # TODO
            # Trzeba dodać zajmowanie się blokami - zapisać oraz zaktualizować odpowiednio strukturę blockList
            # print(message)
            block_data = message[message.find(":", message.find(":")+1):]
            block_dict = json.loads(block_data)
            block = blockList.Block.from_dict(block_dict)
            if block_list.add_block(block):
                log_text = f"Received block with entries: {[x.entry_id for x in block.list_of_entries]} \n"
                print(log_text)
                new_log(log_text)
            else:
                log_text = f"Received INVALID block with entries: {[x.entry_id for x in block.list_of_entries]} \n"
                print(log_text)
                new_log(log_text)

    except Exception as e:
        log_text = f"Error during file reception: {e}"
        print(log_text)
        new_log(log_text)


def initialize_server():
    global server_ip, server_port, temporary_dir

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

    ## remove logs from previous usage
    file_path = "log.txt"
    if os.path.exists(file_path):
        os.remove(file_path)
        log_text = "Removed logs from previous usage"
        print(log_text)
        new_log(log_text)


def send_signal_to_neighbors(server_socket, node_list, signal):
    for node in node_list.nodes:
        print(f"Sending {signal} to {node.ip}:{node.port}")
        msg = signal
        server_socket.sendto(msg.encode(), (node.ip, int(node.port)))


def check_input():
    files = [file for file in os.listdir("input")]
    if len(files) == 0:
        log_text = "No files in input directory"
        print(log_text)
        log_text = "No files in input directory"
        ##new_log(log_text)
        return False
    else:
        log_text = f"Files: {files} in directory"
        new_log(log_text)
    return True


def send_input(node_list, entry_list):
    files = sorted(os.listdir("input"))
    for file in files:
        print(f"File input: {file}")
        anySent = False

        uuidStr = str(uuid.uuid4())

        for node in node_list.nodes:
            if not node.online:
                continue

            print(f"Sending {file} to {node.ip}:{node.port}")
            # send_data(node, "autor", "test", f"input/{file}")
            # Zastanowić się gdzie trzymać autora

            sent = send_entry(node, uuidStr, author_id="autor",
                              file_path=f"input/{file}")
            if sent:
                node_list.set_online(node.ip, node.port, True)
                anySent = True

                ## loging
                log_text = f"File {file} sent to {node.ip}:{node.port} \n"
                new_log(log_text)
            else:
                node_list.set_online(node.ip, node.port, False)

        if anySent:

            file_data = open(f"input/{file}", "r", encoding="utf-8").read()

            entry_dict = {
                "entry_id": uuidStr,
                "author_id": "autor",
                "data": file_data
            }

            file_name = f"""entries/received_{entry_dict["entry_id"]}.json"""
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(entry_dict, f)

            os.remove(f"input/{file}")


def listen(node_list, block_list):
    try:
        server_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((server_ip, int(server_port)))
        server_socket.listen(5)
        server_socket.settimeout(1)  # być może mniej

        conn, addr = server_socket.accept()
        # print(f"Connection from {addr}")

        data = conn.recv(1024)
        # print(f"Received data from {addr}: {data}")
        if data[:4] == b"PING":
            conn.send(b"pong")
            node_list.set_online(addr[0], addr[1], True)
            log_text = f"Sent pong to {addr[0]}:{addr[1]}"
            print(log_text)
            new_log(log_text)

        if data.startswith(b"ENTRY:") or data.startswith(b"BLOCK:"):
            receive_file(data, addr, block_list)

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
        log_text = f"PING[{server_ip}:{server_port}]: Failed while connecting to  {node.ip}: {node.port}: {e}"
        print(log_text)
        new_log(log_text)
        return

    # send ping to node
    # wait for response
    # return True if response received, False otherwise
    try:
        server_socket.send(b"PING")
        server_socket.settimeout(random.randint(3, 5))
        response = server_socket.recv(1024)
        if response.decode() == "pong":
            log_text = f"Received pong from {node.ip}:{node.port}"
            print(log_text)
            new_log(log_text)
            return True
        else:
            log_text = f"Unexpected response: {response.decode()}"
            print(log_text)
            new_log(log_text)
            return False
    except socket.timeout:
        log_text = f"Ping to {node.ip}:{node.port} timed out"
        print(log_text)
        new_log(log_text)
        return False
    except Exception as e:
        log_text = f"Error during ping: {e}"
        print(log_text)
        new_log(log_text)
        return False
    finally:
        server_socket.close()


def fake_ping(node_list):
    for node in node_list.nodes:
        if node.online:
            continue
        node_list.set_online(node.ip, node.port, True)


def on_exit():
    # do cleanup
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

    entry_list = entryList.EntryList()
    # entry_list.from_dir("entries")

    block_list = blockList.BlockList().load()

    start_settigs = textwrap.dedent(f'''
    Node list: {node_list}
    User list: {user_list}
    {block_list}
    ''')
    print(start_settigs)
    new_log(start_settigs)

    print("Configuration finished")
    print("Starting loop, send SIGINT to stop (Ctrl+C)")
   # send_signal_to_neighbors(server_socket, node_list, "START")

    for node in node_list:
        node_list.set_online(node.ip, node.port, False)

    sampling_time = 2
    last_time = time.time()

    try:
        while running:
            # TODO Rework, listen ma pauzować pętle
            current_time = time.time()
            if current_time - last_time >= sampling_time:
                listen(node_list, block_list)
                # ping offline nodes
                # ping(node_list)
                fake_ping(node_list)

                # Check if we have any files in the input directory
                if check_input():
                    log_text = "New file in input folder"
                    print(log_text)
                    new_log(log_text)
                    send_input(node_list, entry_list)

                # Check if we have enough entries to create a block
                if len(os.listdir("entries")) >= limit_of_entries:
                    log_text = "Limit of entries reached"
                    print(log_text)
                    new_log(log_text)
                    create_block(block_list)
                    send_latest_block_to_neighbors(node_list, block_list)

                last_time = current_time

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if not temporary_dir:
            print("Saving data")
            block_list.save()
            node_list.to_file("nodes/nodes.json")
            user_list.to_file("users/users.json")

        log_text = f'''
        Block list:
        {block_list.pretty_print()}
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
