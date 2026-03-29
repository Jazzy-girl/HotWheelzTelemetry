from queue import Full
import cantools, can
import cantools.database
from bitstring import BitArray


VALID_IDs = [
    # UPDATED
    '02B',
    '02C'
]


# LATEST_DBC.dbc holds the latest dbc file
# test_26.txt holds 2 test lines of data
# LATEST_DATA.txt holds the most updated data

DBC_FILE = 'Experimentation/DBC Data/LATEST_DBC.dbc'
SIM_DATA_FILE = 'Experimentation/ReadingData/TestData/CANData1/LATEST_DATA.txt'

FIELDS = {
    'PackSOC',
    'PackCurrent',
    'PackInstVoltage',
    'HighTemp',
    'LowTemp',
    'Low Cell Voltage Fault',
    'Current Sensor Fault',
    'Pack Voltage Sensor Fault',
    'Thermistor Fault'
}

# Values in ERROR_DICT are identical to the last 4 fields in FIELDS.
# ERROR_DICT is used for checking Custom Flag's first 4 bits for errors and updating the 'information' dict.
ERROR_DICT = {
    0: 'Low Cell Voltage Fault',
    1: 'Current Sensor Fault',
    2: 'Pack Voltage Sensor Fault',
    3: 'Thermistor Fault'
}

information = dict()
for field in FIELDS:
    information[field] = 0

# Load the DBC file
db = cantools.database.load_file(DBC_FILE)

# Load data fike
with open(SIM_DATA_FILE, 'r') as file:
    i = 0
    for line in file:
        # Process each line
        # first letter is useless
        # next three are the hex
        # next char is useless
        # final chars are the data
        hex_string = line[1:4]
        
        id = int(hex_string, 16)
        i+=1
        if(i == 10):
            break

        if(hex_string in VALID_IDs):
            data = bytes.fromhex(line[5:])
            message = db.decode_message(id, data)
            #print(f"Thermistor Temp: {message['ThermistorValue']} degrees Celsius")
            for key in message.keys():
                information[key] = message[key]
                """
                The following if statement converts the CustomFlag hex data into binary and checks
                the first 4 bits for 1's, as the Custom Flag id sends 1-byte message where the first 4 bits each
                represent a possible error (see ERROR_DICT for the order)
                """
                if (key == 'CustomFlag'):
                    bits = BitArray(message[key].to_bytes()).bin
                    for index in range(0, 4):
                        if bits[index] == '1': # if there IS an error
                            information[ERROR_DICT[index]] = 1
                    continue
            #print(information)
            print(message)
