import serial
import time

# Configure the serial connection to the GPS
gps_serial = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)

# Function to enable antenna status reports
def enable_antenna_report():
    # PMTK command: 314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0
    cmd = b'$PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0*2C\r\n'
    gps_serial.write(cmd)

# Function to check antenna status
def check_antenna():
    enable_antenna_report()
    while True:
        line = gps_serial.readline().decode('ascii', errors='ignore')
        #print(line)
        if line.startswith('$PGTOP'):
            parts = line.split(',')
            if len(parts) >= 2:
                status = parts[1]
                if status == '3':
                    return "External Active Antenna"
                elif status == '2':
                    return "Internal Patch Antenna"
                elif status == '1':
                    return "Antenna Short Circuit/Error"
            break
    return "Unknown Status"

# Main loop
try:
    print("Checking antenna...")
    print(f"Status: {check_antenna()}")
except KeyboardInterrupt:
    gps_serial.close()
