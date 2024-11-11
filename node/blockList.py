from typing import List, Optional

class Block:
    def __init__(self, data, prev_block: Optional['Block'] = None, next_block: Optional['Block'] = None):
        self.data = data
        self.prev_block = prev_block
        self.next_block = next_block

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
