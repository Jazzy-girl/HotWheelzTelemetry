import cantools

# Load the DBC file
db = cantools.database.load_file("Experimentation\DBC Data\start2.dbc")

# Print all message CAN IDs in the database
print("Messages in DBC file:")
for message in db.messages:
    print(f"ID: {hex(message.frame_id)} - Name: {message.name}")
