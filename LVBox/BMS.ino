#include "BMS.h"
#include "packet.h"
#include <Wire.h>

#define FEATHER_ADDRESS 0x52
#define I2C_FRAME_LEN 25
#define BMS_SDA A2
#define BMS_SCL A3
#define WIRE_TIMEOUT 100 // microseconds
#define WIRE_RESET true

/// Initialize the I2C connection
void bms_init() {
    Wire.setSDA(BMS_SDA);
    Wire.setSCL(BMS_SCL);
    Wire.setWireTimeout(WIRE_TIMEOUT, WIRE_RESET);
    Wire.begin();
}
/// Read the I2C data into the global packet
void bms_poll() {
    Wire.requestFrom(FEATHER_ADDRESS, I2C_FRAME_LEN);
    switch Wire.readBytes((uint8_t*)(&PACKET.faults), I2C_FRAME_LEN) {
    case 0: break; // no data was received
    case I2C_FRAME_LEN: // we got a full packet
        swap_packet_bytes();
        break;
    // TODO: handle a default case?
    }
}
