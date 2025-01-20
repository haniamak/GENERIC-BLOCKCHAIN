from typing import List, Optional
from entryList import Entry, EntryList
import json
import hashlib


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
        return hashlib.sha256(self.__str__().encode()).hexdigest()

    def __str__(self):
        return f"Block data: {self.list_of_entries.to_dict()}"

    def __repr__(self):
        return self.__str__()


class BlockList:
    def __init__(self, block_list: Optional[List[Block]] = None) -> None:
        if block_list is None:
            block_list = []
        self.block_list = block_list
        self.branch_list = []

    def is_empty(self) -> bool:
        return not bool(self.block_list)

    def add_block(self, block: Block) -> bool:
        if block.next_block is not None:
            raise TypeError("Block has defined next element - should be None")

        if self.branch_list:
            for branch in self.branch_list:
                if block.prev_block == branch.hash():
                    # block extends the tree, so we delete other branches
                    try:
                        self.block_list[-1].next_block = block.hash()
                    except IndexError:
                        pass
                    self.block_list.append(branch)
                    self.branch_list = [block]
                    return True

            if len(self.block_list) == 0:
                if block.prev_block is None:
                    # block is diffrent root
                    self.branch_list.append(block)
                    return True
                # block is invalid
                return False

            if block.prev_block != self.block_list[-1].hash():
                # block is invalid
                return False

            # block is a diffrent branch
            self.branch_list.append(block)
            return True

        else:
            # the first block
            self.branch_list.append(block)
            return True

    def save(self, path="blocks/block.json") -> None:
        # TODO: save branch list
        data = []
        for block in self.block_list:
            data.append(block.to_dict())
        with open(path, "w") as file:
            json.dump(data, file)

    def load(self, path="blocks/block.json"):
        with open(path, 'r') as file:
            data = json.load(file)
            self.block_list = []
            prev = None
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

    def pretty_print(self):
        log = "Blocks: \n"
        for block in self.block_list:
            log += block.pretty_print() + "\n"
        log += "Branches: \n"
        for branch in self.branch_list:
            log += branch.pretty_print() + "\n"
        return log

    def last_block(self):
        if len(self.branch_list) == 1:
            return self.branch_list[0]

        if len(self.branch_list) == 0:
            if len(self.block_list) == 0:
                return None
            return self.block_list[-1]

        raise ValueError("There are more than one branch")

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
