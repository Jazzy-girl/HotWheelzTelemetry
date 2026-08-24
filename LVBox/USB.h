#ifndef USB_H
#define USB_H
#include "packet.h"

/// Initialize serial buffers
void serial_init();
/// Send the packet over serial
void send_serial();
#endif
