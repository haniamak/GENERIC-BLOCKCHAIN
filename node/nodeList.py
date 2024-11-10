class Node:
    def __init__(self, ip: str):
        self.ip = ip

    def __str__(self):
        return self.ip


class NodeList:
    def __init__(self):
        self.nodes = []

    def addNode(self, ip):
        self.nodes.append(Node(ip))

    def __str__(self):
        return '\n'.join([str(node) for node in self.nodes])
