import serial
import os
import sys
import io
import base64
import math

sys.path.append(os.path.join(os.path.split(__file__)[0], ".."))
import packet

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print(f"Usage: {sys.argv[0]} <PORT | FILE> [baudrate]")
    sys.exit(1)

port = sys.argv[1]
baud = int(sys.argv[2]) if len(sys.argv) == 3 else 9600

if not os.path.exists(port):
    print(f"{port} does not exist")
    sys.exit(2)

def load_serial() -> io.TextIOWrapper:
    ser = serial.Serial(port, baud)
    ser.open()
    return io.TextIOWrapper(io.BufferedReader(ser), newline='\n')

interface = open(port) if os.path.isfile(port) else load_serial()

for line in interface:
    if len(line) == 0:
        print()
    elif line[0] == '!':
        if line[-1] == '\n':
            line = line[:-1]
        print("Text:", line[1:])
    else:
        print("Escaped:", line)
        data = base64.decodebytes(line.encode('ascii'))
        print("Hex:", data.hex(" "))
        if len(data) == 56 and data[:2] == b"HW":
            print("Decoded data:")
            raw = packet.RawPacket.unpack_bytes(data)
            checksum = packet.checksum_of_data(data)
            pack = raw.parse()
            print("Header:")
            print(f"  Provided checksum:   {hex(pack.checksum)}")
            print(f"  Calculated checksum: {hex(checksum)}")
            print(f"  Checksums match:     {pack.checksum == checksum}")
            print(f"  Timestamp:           {pack.timestamp} ms")
            print("GPS:")
            print(f"  Longitude:           {pack.gps_lon}°")
            print(f"  Latitude:            {pack.gps_lat}°")
            print("Cockpit temperature:")
            print(f"  Raw reading:         {pack.therm_reading}")
            print(f"  Voltage:             {pack.therm_voltage} V")
            print(f"  Resistance:          {pack.therm_resistance} Ω")
            print(f"  Temperature:         {pack.therm_temp}°C")
            print("Speed:")
            print(f"  GPS speed:           {pack.gps_speed} mph")
            print(f"  Motor speed:         {pack.motor_speed} mph")
            print("BMS data:")
            print(f"  Pack current:        {pack.bms_current} A")
            print(f"  Pack open voltage:   {pack.bms_open_voltage} V")
            print(f"  Pack summed voltage: {pack.bms_summed_voltage} V")
            print(f"  12V input voltage:   {pack.bms_supply_12v} V")
            print(f"  High cell:           cell {pack.bms_high_cell_id:3}, {pack.bms_high_cell_volt} V")
            print(f"  Low cell:            cell {pack.bms_low_cell_id:3}, {pack.bms_low_cell_volt} V")
            print(f"  High temp:           therm {pack.bms_high_therm_id:3}, {pack.bms_high_temp}°C")
            print(f"  Low temp:            therm {pack.bms_low_therm_id:3}, {pack.bms_low_temp}°C")
            print(f"  Pack SoC:            {pack.bms_soc}%")
            print(f"  Fan speed:           {pack.fan_speed}")
            print(f"  Faults:              {pack.lo_faults.bit_count() + pack.hi_faults.bit_count()}")
        else:
            print("Unknown data")