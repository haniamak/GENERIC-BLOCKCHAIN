import socket
import os
import json
import random
from helpers import print_and_log
from main import *
import hashlib

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
        print_and_log(f"PING[{server_ip}:{server_port}]: Failed while connecting to " +
              f"{node.ip}: {node.port}: {e}!")
        return

    # send ping to node
    # wait for response
    # return True if response received, False otherwise
    try:
        server_socket.send(b"PING")
        server_socket.settimeout(random.randint(3, 5))
        response = server_socket.recv(1024)
        if response.decode() == "pong":
            print_and_log(f"Received pong from {node.ip}:{node.port}!")
            return True
        else:
            print_and_log(f"Unexpected response: {response.decode()}!")
            return False
    except socket.timeout:
        print_and_log(f"Ping to {node.ip}:{node.port} timed out!")
        return False
    except Exception as e:
        print_and_log(f"Error during ping: {e}!")
        return False
    finally:
        server_socket.close()


def fake_ping(node_list):
    for node in node_list.nodes:
        if node.online:
            continue
        node_list.set_online(node.ip, node.port, True)


def send_signal_to_neighbors(server_socket, node_list, signal):
    for node in node_list.nodes:
        print_and_log(f"Sending {signal} to {node.ip}:{node.port}.")
        msg = signal
        server_socket.sendto(msg.encode(), (node.ip, int(node.port)))


def receive_file(data, addr, block_list):
    try:
        try:
            message = data.decode()
        except Exception as e:
            print_and_log(f"Error decoding data from {addr}: {e}!")
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
                print_and_log(f"Warning: Expected file size {file_size}, but received {len(file_data)} bytes.")

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
            print_and_log(f"Received file: {file_name}, Entry ID: " + \
                f"{entry_id}, Author ID: {author_id}, From: {addr}")

        elif message.startswith("BLOCK:"):
            # print_and_log("Received block")
            block_data = message[message.find(":", message.find(":")+1)+1:]
            # print_and_log(f"Block data: {block_data}")
            block_dict = json.loads(block_data)
            block = blockList.Block()
            block.from_dict(block_dict)
            if block_list.add_block(block):
                print_and_log(f"Received block of hash {block.hash()} child of {block.prev_block}.\n")
            else:
                print_and_log(f"Received INVALID block of hash {block.hash()} child of {block.prev_block}.\n")

        else:
            print_and_log(f"Received unknown message: {message}.")

    except Exception as e:
        print_and_log(f"Error during file reception: {e}!")


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

                print_and_log(f"Sent block {[x.entry_id for x in latest_block.list_of_entries.entries]} to {node.ip}:{node.port}.")

            except Exception as e:
                print_and_log( f"FAILED: Sent block {[x.entry_id for x in latest_block.list_of_entries.entries]} to {node.ip}:{node.port}\n {e}!")


def send_entry(node, hash_str, author_id, file_path):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(SEND_TIMEOUT)

    try:
        server_socket.connect((node.ip, int(node.port)))
    except Exception as e:
        print_and_log(f"Failed while connecting to {node.ip}:{node.port}: {e}!")
        return False

    try:
        if not os.path.exists(file_path):
            print_and_log(f"File not found: {file_path}.")
            return False

        with open(file_path, "rb") as file:
            file_data = file.read()

        entry_id = hash_str
        msg = f"ENTRY:{len(file_data)}:{entry_id}:{author_id}:"
        full_message = msg.encode() + file_data

        print_and_log(f"Sending file with message to {node.ip}:{node.port}.")

        server_socket.send(full_message)
    except socket.timeout:
        print_and_log(f"Timeout while sending file to {node.ip}:{node.port}.")
        return False
    except Exception as e:
        print_and_log(f"Error during file transmission: {e}!")
        return False
    finally:
        server_socket.close()
        return True


def check_input():
    if len(os.listdir("input")) == 0:
        print_and_log("No files in input directory.", with_log=False)
        return False
    return True


def send_input(node_list):
    files = sorted(os.listdir("input"))
    for file in files:
        print_and_log(f"File input: {file}")
        any_sent = False

        hash_str = str(hashlib.sha256(file.encode()).hexdigest())

        for node in node_list.nodes:
            if not node.online:
                continue

            print_and_log(f"Sending {file} to {node.ip}:{node.port}")

            sent = send_entry(node, hash_str, author_id="autor",
                              file_path=f"input/{file}")
            if sent:
                node_list.set_online(node.ip, node.port, True)
                any_sent = True

                print_and_log(f"File {file} sent to {node.ip}:{node.port}")
            else:
                node_list.set_online(node.ip, node.port, False)

        if any_sent:
            file_data = open(f"input/{file}", "r", encoding="utf-8").read()

            entry_dict = {
                "entry_id": hash_str,
                "author_id": "autor",
                "data": file_data
            }

            file_name = f"""entries/received_{entry_dict["entry_id"]}.json"""
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(entry_dict, f)

            os.remove(f"input/{file}")
