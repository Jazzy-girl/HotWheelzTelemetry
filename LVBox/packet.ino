#include "packet.h"

packet_t packet;

/// Swap the byte order in an integer
void swap_bytes_u16(uint16_t* val) {
    uint8_t temp = (int8_t)(*val);
    *val >>= 8;
    *val |= (uint16_t)temp << 8;
}

/// Swap all of the BE ints in the packet to LE
void swap_packet_bytes(packet_t* packet) {
    swap_bytes_u16((uint16_t*)(&packet->pack_current));
    swap_bytes_u16(&packet->pack_open_voltage);
    swap_bytes_u16(&packet->pack_summed_voltage);
    swap_bytes_u16(&packet->supply_12v);
    swap_bytes_u16(&packet->high_cell_voltage);
    swap_bytes_u16(&packet->low_cell_voltage);
}

/// Write the checksum to the packet
void write_checksum(packet_t* packet) {
    uint16_t* checksum = &packet->checksum;
    uint16_t* start = checksum;
    const uint16_t* end = (uint16_t*)(packet + 1);
    while (++start != end) *checksum ^= *start;
}