from typing import List, Optional
from entryList import Entry, EntryList
import json


class Block:
    def __init__(self, list_of_entries: Optional['EntryList'] = None, prev_block: Optional['Block'] = None, next_block: Optional['Block'] = None):
        self.list_of_entries = list_of_entries
        self.prev_block = prev_block
        self.next_block = next_block

    def to_dict(self):
        return {
            'entries': self.list_of_entries.to_dict()
        }

    def __str__(self):
        return f"Block data: {self.list_of_entries.to_dict()}"


class BlockList:
    def __init__(self, block_list: Optional[List[Block]] = None) -> None:
        if block_list is None:
            block_list = []
        self.block_list = block_list

    def is_empty(self) -> bool:
        return not bool(self.block_list)

    def add_block(self, block: Block) -> None:
        if block.next_block is not None:
            raise TypeError("Block has defined next element - should be None")

        if self.block_list:
            last_block = self.block_list[-1]
            last_block.next_block = block
            block.prev_block = last_block
        self.block_list.append(block)

    def save(self, path="blocks/block.json") -> None:
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
                    list_of_entries.add_entry(Entry(entry["entry_id"], entry["author_id"], entry["data"], entry["previous_entries"], entry["encryption_key"]))
                block = Block(list_of_entries = list_of_entries, prev_block=prev)

                if len(self.block_list) != 0:
                    self.block_list[-1].next_block = block
                self.block_list.append(block)
                prev = block
        return self

    def __getitem__(self, index: int) -> Block:
        return self.block_list[index]

    def __str__(self) -> str:
        text = "List of blocks: \n"
        for block in self.block_list: text += str(block) + "\n"
        return text


