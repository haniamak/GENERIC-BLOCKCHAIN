from typing import List, Optional
from entryList import Entry, EntryList
import json
import hashlib
import os


class Block:
    def __init__(self, list_of_entries: Optional['EntryList'] = None, prev_block=None, next_block=None):
        self.list_of_entries = list_of_entries
        self.prev_block = prev_block
        self.next_block = next_block

    def to_dict(self):
        return {
            'entries': self.list_of_entries.to_dict(),
            'prev_block': self.prev_block,
            'next_block': self.next_block
        }

    def from_dict(self, data):
        self.list_of_entries = EntryList()
        for entry in data["entries"]:
            self.list_of_entries.add_entry(Entry(
                entry["entry_id"], entry["author_id"], entry["data"], entry["previous_entries"], entry["encryption_key"]))
        self.prev_block = data["prev_block"]
        self.next_block = data["next_block"]

    def pretty_print(self):
        return f"prev_block: {self.prev_block},\nthis_block: {self.hash()}"

    def hash(self):
        string = str(self.list_of_entries.hash() + str(self.prev_block))
        return hashlib.sha256(string.encode()).hexdigest()

    def __str__(self):
        return f"Block data: {self.list_of_entries.to_dict()}"

    def __repr__(self):
        return self.__str__()


class BlockList:
    def __init__(self, block_list: Optional[List[Block]] = None) -> None:
        self.tree = Tree()
        if block_list is None:
            self.block_list = []
        else:
            self.block_list = []
            for block in block_list:
                self.add_block(block)

    def is_empty(self) -> bool:
        return not bool(self.block_list)

    def add_block(self, block: Block) -> bool:
        if block.next_block is not None:
            raise TypeError("Block has defined next element - should be None")

        tree_node = TreeNode(block)
        if self.is_empty():
            self.block_list.append(block)
            self.tree.add_block(tree_node)
        else:
            self.tree.add_block(tree_node)
            longest_path = self.tree.longest_path()
            print(longest_path)
            self.block_list = longest_path

    def save(self, path="blocks/") -> None:
        for block in self.block_list:
            data = []
            data.append(block.to_dict())
            filename = f"{block.hash()}.json"
            file_path = os.path.join(path, filename)
            with open(file_path, "w") as file:
                json.dump(data, file)

    def load(self, path="blocks/"):
        files = os.listdir(path)
        self.block_list = []
        prev = None
        for filename in files:
            file_path = os.path.join(path, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
                for block_data in data:
                    list_of_entries = EntryList()
                    for entry in block_data["entries"]:
                        list_of_entries.add_entry(Entry(
                            entry["entry_id"], entry["author_id"], entry["data"], entry["previous_entries"], entry["encryption_key"]))
                    block = Block(list_of_entries=list_of_entries,
                                  prev_block=prev.hash() if prev else None)

                    if len(self.block_list) != 0:
                        self.block_list[-1].next_block = block.hash()
                    self.block_list.append(block)
                    prev = block
        return self

    def return_entries(self, block: Block) -> None:
        for entry in block.list_of_entries.entries:
            entry_dict = entry.to_dict()
            file_name = f"""entries/received_{entry_dict["entry_id"]}.json"""
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(entry_dict, f)

    def pretty_print(self):
        log = "Blocks: \n"
        for block in self.block_list:
            log += block.pretty_print() + "\n"
        log += "Branches: \n"
        for branch in self.block_list:
            log += branch.pretty_print() + "\n"
        return log

    def last_block(self):
        if len(self.block_list) == 0:
            return None

        return self.block_list[-1]

    def last_hash(self):
        last = self.last_block()
        if last:
            return last.hash()
        return None

    def __getitem__(self, index: int) -> Block:
        return self.block_list[index]

    def __str__(self) -> str:
        text = "List of blocks: \n"
        for block in self.block_list:
            text += str(block) + "\n"
        return text

    def __len__(self) -> int:
        return len(self.block_list)


class TreeNode:
    def __init__(self, block: Block, parent: Optional['TreeNode'] = None):
        self.block = block
        self.parent = parent
        self.children = []

    def hash(self):
        return self.block.hash()

    def add_child(self, child: 'TreeNode'):
        self.children.append(child)

    def __str__(self):
        return f"TreeNode(block={self.block.hash()})"


class Tree:
    def __init__(self, root: Optional[TreeNode] = None):
        self.root = root
        self.all_nodes = {}

    def add_block(self, tree_block: TreeNode):
        if not self.root:
            self.root = tree_block
            self.all_nodes[tree_block.hash()] = tree_block

        else:
            try:
                tree_block_parent = self.all_nodes[tree_block.block.prev_block]
                self.all_nodes[tree_block_parent.hash()].children.append(
                    tree_block)
                self.all_nodes[tree_block.hash()] = tree_block
            except KeyError:
                print("Invalid Block - no parent in tree")

    def longest_path(self):
        def rec(current_path, tree_block):
            if tree_block is None:
                return current_path
            else:
                new_path = current_path + [tree_block.block]
                children_paths = [
                    rec(new_path, child)
                    for child in self.all_nodes[tree_block.hash()].children
                ]
                return max(children_paths, key=len) if children_paths else new_path

        return rec([], self.root)

    def print_longest_path(self):
        path = self.longest_path()
        print("Longest path:")
        for i, block in enumerate(path):
            print(f"{i}: {block.hash()}")

    def pretty_print(self):
        def rec(tree_block, level):
            if tree_block is None:
                return ""
            str = "  " * level + f"{tree_block.hash()}\n"
            for child in tree_block.children:
                str += rec(child, level + 1)
            return str

        return rec(self.root, 0)
