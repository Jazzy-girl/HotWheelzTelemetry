#include "packet.h"

padded_packet_t padded;

/// Swap the byte order in an integer
void swap_bytes_u16(uint16_t* val) {
    uint8_t temp = (int8_t)(*val);
    *val >>= 8;
    *val |= (uint16_t)temp << 8;
}

/// Swap all of the BE ints in the packet to LE
void swap_packet_bytes() {
    swap_bytes_u16((uint16_t*)(&PACKET.pack_current));
    swap_bytes_u16(&PACKET.pack_open_voltage);
    swap_bytes_u16(&PACKET.pack_summed_voltage);
    swap_bytes_u16(&PACKET.supply_12v);
    swap_bytes_u16(&PACKET.high_cell_voltage);
    swap_bytes_u16(&PACKET.low_cell_voltage);
}

/// Write the checksum to the packet
void write_checksum() {
    uint16_t* checksum = &PACKET.checksum;
    uint16_t* start = checksum;
    const uint16_t* end = (uint16_t*)(&PACKET + 1);
    while (++start != end) *checksum ^= *start;
}