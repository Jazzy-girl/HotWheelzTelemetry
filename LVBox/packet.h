#ifndef PACKET_H
#define PACKET_H

#include <stdint.h>

typedef struct packet {
    uint8_t H;
    uint8_t W;
    uint16_t checksum;
    uint32_t timestamp;
    double longitude;
    double latitude;
    int16_t cockpit_temp;
    uint16_t motor_speed;
    float gps_speed;
    int32_t faults;
    int16_t pack_current;
    uint16_t pack_open_voltage;
    uint16_t pack_summed_voltage;
    uint16_t supply_12v;
    uint16_t high_cell_voltage;
    uint16_t low_cell_voltage;
    uint8_t high_cell_id;
    uint8_t low_cell_id;
    uint8_t high_temp;
    uint8_t low_temp;
    uint8_t high_therm_id;
    uint8_t low_therm_id;
    uint8_t pack_soc;
    uint8_t fan_speed;
} packet_t;

/// Swap the byte order in an integer
void swap_bytes_u16(uint16_t* val);

/// Swap all of the BE ints in the packet to LE
void swap_packet_bytes(packet_t* packet);

/// Write the checksum to the packet
void write_checksum(packet_t* packet);

#endif // PACKET_H