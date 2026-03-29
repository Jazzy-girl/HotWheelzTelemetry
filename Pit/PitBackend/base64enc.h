
#define B64_SIZE (BIN_SIZE * 4 + 2) / 3

// the alphabet string for base64
const char* ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

// the input, binary buffer
char binBuf[BIN_SIZE];
// the output, base64 buffer, which will be null-terminated
char b64Buf[B64_SIZE + 1];

// read data from binBuf and write it to b64Buf, with a buffer length of bytes
void encodeBase64(unsigned char bytes) {
    char* readPtr = binBuf;
    char* writePtr = b64Buf;
    char a, b, c;
    LOOP_START:
    switch (bytes) {
        case 0: break;
        case 1:
            a = readPtr[0];
            writePtr[0] = ALPHABET[a >> 2];
            writePtr[1] = ALPHABET[(a & 0x03) << 4];
            writePtr += 2;
            break;
        case 2:
            a = readPtr[0];
            b = readPtr[1];
            writePtr[0] = ALPHABET[a >> 2];
            writePtr[1] = ALPHABET[((a & 0x03) << 4) | (b >> 4)];
            writePtr[2] = ALPHABET[(b & 0x03) << 4];
            writePtr += 3;
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
            bytes -= 3;
            goto LOOP_START;
    }
    *writePtr = 0;
}