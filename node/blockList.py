from typing import List, Optional
import json

class Block:
    def __init__(self, data, prev_block: Optional['Block'] = None, next_block: Optional['Block'] = None):
        self.data = data
        self.prev_block = prev_block
        self.next_block = next_block


    def save(self, filename = "block.json"):
        def to_dict(self):
            return {
                'data': self.data,
                'prev_block': self.prev_block.data if self.prev_block else None,
                'next_block': self.next_block.data if self.next_block else None
            }

        try:
            with open(filename, 'r') as file:
                blocks = json.load(file)
        except FileNotFoundError:
            blocks = []

        blocks.append(to_dict(self))

        with open(filename, 'w') as file:
            json.dump(blocks, file, indent=4)
    
    def read(self, filename = "block.json"):
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print("No block file found.")
            return []

    def __str__(self):
        return f"Block data: {self.data}"

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

    def __getitem__(self, index: int) -> Block:
        return self.block_list[index]

    def __str__(self) -> str:
        text = "List of blocks: \n"
        for block in self.block_list: text += str(block) + "\n"
        return text
