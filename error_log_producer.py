import re
from kafka import KafkaProducer
import time

log_file = "excel_to_sqlite.log"   # change path if needed
producer = KafkaProducer(bootstrap_servers="localhost:9092")

def extract_new_error_blocks(log_path, last_position=0):
    error_blocks = []
    with open(log_path, "r", encoding="utf-8") as f:
        f.seek(last_position)
        lines = f.readlines()
        new_position = f.tell()

    block = []
    in_error = False
    log_entry_pattern = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - ")

    for line in lines:
        if " - ERROR - " in line:
            if block:
                error_blocks.append("".join(block))
                block = []
            in_error = True
            block.append(line)
        elif in_error:
            if log_entry_pattern.match(line) and " - ERROR - " not in line:
                error_blocks.append("".join(block))
                block = []
                in_error = False
            else:
                block.append(line)
    if block:
        error_blocks.append("".join(block))
    return error_blocks, new_position

# Example usage in your producer loop:
log_path = "excel_to_sqlite.log"
last_position = 0

with open(log_file, "r") as f:
    # go to end of file
    f.seek(0, 2)

    while True:
        error_blocks, last_position = extract_new_error_blocks(log_path, last_position)
        for error_block in error_blocks:
            producer.send('error-logs', error_block.encode('utf-8'))

