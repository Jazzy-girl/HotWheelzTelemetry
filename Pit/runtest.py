from PitFrontend.dataLogging import logdata

from packet import ParsedPacket
FILENAME = 'carData.csv'
checksum = 1
timestamp = 1
therm_reading = 1
bms_hi_temp = 1
bms_lo_temp  = 1
bms_avg_temp  = 1
bms_heatsink_temp = 1
gps_lon = 1.0
gps_lat = 1.0
therm_voltage = 1.0
therm_resistance = 1.0
therm_temp = 1.0
bms_current = 1.0
bms_voltage = 1.0
bms_soc = 1.0
bms_health = 1.0
bms_amphours = 1.0
gps_speed = 1.0
motor_speed = 1.0
fault_low_cell_voltage = False
fault_current_sensor = True
fault_pack_voltage = True
fault_thermistor = True

testPacket = ParsedPacket(checksum, timestamp, gps_lon, gps_lat
                          , therm_reading, therm_voltage, therm_resistance,
                          therm_temp, bms_current, bms_voltage, bms_soc,
                          bms_health, bms_amphours, bms_hi_temp, bms_lo_temp,
                          bms_avg_temp, bms_heatsink_temp, fault_low_cell_voltage,
                          fault_current_sensor, fault_pack_voltage, fault_thermistor, gps_speed,
                          motor_speed)

logdata(testPacket)