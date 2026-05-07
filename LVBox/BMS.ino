#include "BMS.h"
#include "packet.h"
#include <Wire.h>

#define FEATHER_ADDRESS 0x52
#define I2C_FRAME_LEN 25
#define BMS_SDA A2
#define BMS_SCL A3

/// Initialize the I2C connection
void bms_init() {
    Wire.setSDA(BMS_SDA);
    Wire.setSCL(BMS_SCL);
    Wire.begin();
}
/// Read the I2C data into the global packet
void bms_poll() {
    Wire.requestFrom(FEATHER_ADDRESS, I2C_FRAME_LEN);
    Wire.readBytes((uint8_t*)(&PACKET.faults), I2C_FRAME_LEN);
}
