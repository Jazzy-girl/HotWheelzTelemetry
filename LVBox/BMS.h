#ifndef BMS_H
#define BMS_H

/// Initialize the I2C connection
void bms_init();
/// Read the I2C data into the global packet
void bms_poll();

#endif // BMS_H