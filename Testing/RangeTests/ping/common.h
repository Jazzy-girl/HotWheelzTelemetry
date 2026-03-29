#include <SPI.h>
#include <RH_RF95.h>

#define RF95_FREQ 915.0

RH_RF95 rf(RFM95_CS, RFM95_INT);

const char* HEX_BYTES = "0123456789abcdef";
short COUNTER = 0;

const char* BASE_PING = "HW PING ";
const char* BASE_PONG = "HW PONG ";

#define PREFIX_LEN  8
#define MESSAGE_LEN  12
#define PAYLOAD_LEN 4

#define ERROR_PREFIX_LEN 27

char buf[RH_RF95_MAX_MESSAGE_LEN + 1];
char binaryBuf[RH_RF95_MAX_MESSAGE_LEN * 2 + ERROR_PREFIX_LEN + 1]; // two bytes per char + our message + null

bool isNonPrintable(char ch) {
    return ch < '\n' || ch > '~';
}

void initRadio() {
    pinMode(RFM95_RST, OUTPUT);
    digitalWrite(RFM95_RST, HIGH);
    delay(100);
    digitalWrite(RFM95_RST, LOW);
    delay(10);
    digitalWrite(RFM95_RST, HIGH);
    delay(10);

    while (!rf.init()) {
        Serial.println("Initialization failed!");
        // while (1);
    }

    while (!rf.setFrequency(RF95_FREQ)) {
        Serial.println("Frequency failed!");
        while (1);
    }

    rf.setTxPower(23, false);

    memcpy(binaryBuf, "Unexpected binary message: ", ERROR_PREFIX_LEN);
}

void printUnexpected(uint8_t len) {
    bool isBinary = false;
    char const* bPtr = buf;
    char const* const bEnd = bPtr + len;
    while (bPtr < bEnd) if (isNonPrintable(*bPtr++)) {
        isBinary = true;
        break;
    }
    if (isBinary) {
        char* rPtr = buf;
        char* wPtr = binaryBuf + ERROR_PREFIX_LEN;
        while (rPtr < bEnd) {
            char b = *rPtr++;
            *wPtr++ = HEX_BYTES[b >> 4];
            *wPtr++ = HEX_BYTES[b & 15];
        }
        *wPtr = 0;
        Serial.println(binaryBuf);
    } else {
        buf[len] = 0;
        Serial.print("Unexpected printable message: ");
        Serial.println(buf);
    }
}