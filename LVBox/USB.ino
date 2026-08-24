#include "USB.h"

#define OUTPUT_LEN ((sizeof(packet_t) + 2) / 3) * 4

const char *ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

/*
Base 64 encoding
encodes 3 input bytes into 4 output bytes
size of (((packet_t + 2)/3)*4)
pointer to Uint8
*/

char base64_buffer[OUTPUT_LEN + 2];

/// Initialize serial buffers
void serial_init() {
    Serial.begin(9600);
    base64_buffer[OUTPUT_LEN] = '\n';
    base64_buffer[OUTPUT_LEN + 1] = '\0';
}

/// Send the packet over serial
void send_serial() {
    uint8_t *readPtr = (uint8_t *)(&PACKET);
    char *writePtr = (char *)base64_buffer;
    char a, b, c;
    uint8_t remaining = sizeof(packet_t);
    LOOP_START:
    switch (remaining) {
        case 0: break;
        case 1:
            a = readPtr[0];
            writePtr[0] = ALPHABET[a >> 2];
            writePtr[1] = ALPHABET[(a & 0x03) << 4];
            writePtr[2] = writePtr[3] = '=';
            break;
        case 2:
            a = readPtr[0];
            b = readPtr[1];
            writePtr[0] = ALPHABET[a >> 2];
            writePtr[1] = ALPHABET[((a & 0x03) << 4) | (b >> 4)];
            writePtr[2] = ALPHABET[(b & 0x0f) << 2];
            writePtr[3] = '=';
            break;
        default:
            a = readPtr[0];
            b = readPtr[1];
            c = readPtr[2];
            writePtr[0] = ALPHABET[a >> 2];
            writePtr[1] = ALPHABET[((a & 0x03) << 4) | (b >> 4)];
            writePtr[2] = ALPHABET[((b & 0x0f) << 2) | (c >> 6)];
            writePtr[3] = ALPHABET[c & 0x3f];
            readPtr += 3;
            writePtr += 4;
            remaining -= 3;
            goto LOOP_START;
    }
    Serial.print(base64_buffer);
}
