import json


class Node:
    def __init__(self, ip: str, port: str, online: bool):
        self.ip = ip
        self.port = port
        self.online = online

    def __str__(self):
        return self.ip + ':' + self.port + ' ' + ('online' if self.online else 'offline')


class NodeList:
    def __init__(self):
        self.nodes = []

    def addNode(self, ip, port, online=True):
        self.nodes.append(Node(ip, port, online))

    def removeNode(self, ip, port):
        self.nodes = [node for node in self.nodes if node.ip !=
                      ip and node.port != port]

    def __str__(self):
        return '\n'.join([str(node) for node in self.nodes])

    def toJson(self):
        return json.dumps([{'ip': node.ip, 'port': node.port, 'online': node.online} for node in self.nodes])

    def fromJson(self, jsonStr):
        self.nodes = [Node(node['ip'], node['port'], node['online'])
                      for node in json.loads(jsonStr)]

    def __iter__(self):
        return iter(self.nodes)

    def __len__(self):
        return len(self.nodes)

    def toFile(self, filename):
        with open(filename, 'w') as file:
            file.write(self.toJson())

    def fromFile(self, filename):
        with open(filename, 'r') as file:
            self.fromJson(file.read())
