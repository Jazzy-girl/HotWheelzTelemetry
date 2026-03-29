import re

# log the CAN log file
log_file = 'Experimentation/ReadingData/TestData/CANData1/2025-03-01-14-24-30.txt'

# Regex to match CAN messages
can_pattern = re.compile(r't([0-9A-F]+)([0-9A-F]*)')

# Store parsed data
can_messages = []

with open(log_file, "r") as file:
    for line in file:
        match = can_pattern.match(line.strip())
        if match:
            can_id = match.group(1)  # Extract CAN ID
            data = match.group(2)  # Extract data payload
            print(f"CAN ID: {can_id}, Data: {data if data else 'No Data'}")

