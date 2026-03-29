#define BIN_SIZE 256

#include <stdio.h>
#include <string.h>
#include "base64enc.h"

int main(int argc, char** argv) {
    if (argc < 2) {
        printf("Usage: %s <string>\n", argv[0]);
        return 1;
    }
    strncpy(binBuf, argv[1], BIN_SIZE);
    encodeBase64(strlen(argv[1]));
    puts(b64Buf);
} 