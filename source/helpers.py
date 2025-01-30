from datetime import datetime
import os
import json
import entryList
import blockList

limit_of_entries = 3

def print_and_log(text, with_log=True):
    print(text)
    if with_log:
        log_time = str(datetime.now())[:19]
        with open("log.txt", "a") as log:
            log.write(log_time + " - " + text + "\n")
            log.flush()


def create_block(block_list, save=True):
    list_of_entries = entryList.EntryList()
    entries_id = []
    for filename in os.listdir("entries/")[:limit_of_entries]:
        file_path = os.path.join("entries/", filename)
        with open(file_path, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
            entry = entryList.Entry(
                loaded_data["entry_id"], loaded_data["author_id"], loaded_data["data"])
            list_of_entries.add_entry(entry)
            entries_id.append(loaded_data["entry_id"])
        if os.path.exists(file_path):
            os.remove(file_path)

    block = blockList.Block(list_of_entries)
    block.prev_block = block_list.last_hash()
    block_list.add_block(block)

    log_text = f"Created block with entries: {entries_id}."
    print_and_log(log_text)

    if save:
        block_list.save()

    return block
