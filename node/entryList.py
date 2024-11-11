from typing import List, Optional

class Entry:
    def __init__(
        self,
        entry_id: int,
        author_id: int,
        data: str,
        previous_entries: Optional[List[int]] = None,
        encryption_key: Optional[int] = None,
    ):
        self.id: int = id
        self.entry_id: int = entry_id
        self.author_id: int = author_id
        self.data: str = data
        self.previous_entries: List[int] = previous_entries if previous_entries is not None else []
        self.encryption_key: int = encryption_key
    
    def __str__(self) -> str:
        return f"Entry(entry_id={self.entry_id}, 
                author_id={self.author_id}, 
                data={self.data}, 
                previous_entries={self.previous_entries}, 
                encryption_key={self.encryption_key})"

class EntryList:
    def __init__(self) -> None:
        self.entries: List[Entry] = []

    def __str__(self) -> str:
        return f"EntryList, entries={self.entries}"
    
    def add_entry(self, entry: Entry) -> None:
        self.entries.append(entry)    
    
    # Function removes entry, returns True if removal is succesful, else it returns False
    def remove_entry(self, id: int) -> None:
        for entry in self.entries:
            if entry.id == id:
                self.entries.remove(entry)
                return True
        return False