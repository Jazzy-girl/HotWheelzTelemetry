#ifndef USB_H
#define USB_H
#include "packet.h"

extern char base64_buffer[((sizeof(packet_t) + 2) / 3) * 4];

void sendSerial();
#endif