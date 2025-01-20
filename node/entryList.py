from typing import List, Optional
import json
import os


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
        self.previous_entries: List[int] = previous_entries if previous_entries is not None else [
        ]
        self.encryption_key: int = encryption_key

    def __str__(self) -> str:
        return f'''Entry(entry_id={self.entry_id},
                author_id={self.author_id},
                data={self.data},
                previous_entries={self.previous_entries},
                encryption_key={self.encryption_key})'''

    def to_dict(self):
        return {
            'entry_id': self.entry_id,
            'author_id': self.author_id,
            'data': self.data,
            'previous_entries': self.previous_entries,
            'encryption_key': self.encryption_key
        }

    def from_dict(self, data):
        self.entry_id = data['entry_id']
        self.author_id = data['author_id']
        self.data = data['data']
        self.previous_entries = data['previous_entries']
        self.encryption_key = data['encryption_key']
        return self


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

    def to_dict(self):
        return [x.to_dict() for x in self.entries]

    def to_json(self):
        return json.dumps(self.to_dict())

    def from_json(self, json_str):
        data = json.loads(json_str)
        for entry in data:
            self.add_entry(Entry(
                entry['entry_id'],
                entry['author_id'],
                entry['data'],
                entry['previous_entries'],
                entry['encryption_key']
            ))
        return self

    def to_file(self, file_path):
        with open(file_path, 'w') as file:
            file.write(self.to_json())

    def from_dir(self, dir_path):
        try:
            files = os.listdir(dir_path)
            for file in files:
                with open(file, 'r') as file:
                    entry = Entry.from_dict(json.load(file))
                    self.add_entry(entry)
        except FileNotFoundError:
            return EntryList()
