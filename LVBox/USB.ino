#include "USB.h"

/*
Base 64 encoding
encodes 3 input bytes into 4 output bytes
size of (((packet_t + 2)/3)*4)
pointer to Uint8
*/

char base64_buffer[((sizeof(packet_t) + 2) / 3) * 4];
char *outPtr = (char *)base64_buffer;

const char *ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

void sendSerial()
{
    uint8_t *in = (uint8_t *)(&PACKET);
    int remaining = sizeof(packet_t);
    while (remaining > 0)
    {
        switch (remaining)
        {
        case 1:
            base64_buffer[0] = ALPHABET[in[0] & 0x3F];
            base64_buffer[1] = ALPHABET[in[0] >> 6];
            base64_buffer[2] = base64_buffer[3] = '=';
            break;
        case 2:
            base64_buffer[0] = ALPHABET[in[0] & 0x3F];
            base64_buffer[1] = ALPHABET[(in[0] >> 6) | ((in[1] & 0xF) << 2)];
            base64_buffer[2] = ALPHABET[(in[1] >> 4)];
            base64_buffer[3] = '=';
        default:
            base64_buffer[0] = ALPHABET[in[0] & 0x3F];
            base64_buffer[1] = ALPHABET[(in[0] >> 6) | ((in[1] & 0xF) << 2)];
            base64_buffer[2] = ALPHABET[(in[1] >> 4) | (in[2] & 0x2) << 4];
            base64_buffer[3] = ALPHABET[in[2] >> 2];
        }
        in += 3;
        outPtr += 4;
        remaining -= 3;
    }
    Serial.write(base64_buffer);
}
