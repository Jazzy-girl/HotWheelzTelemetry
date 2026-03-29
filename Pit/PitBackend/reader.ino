#include <SPI.h>
#include <RH_RF95.h>

#define BIN_SIZE RH_RF95_MAX_MESSAGE_LEN

#include "base64enc.h"

#define RFM95_CS   8
#define RFM95_RST  4
#define RFM95_INT  3
#define RF95_FREQ 915.0

RH_RF95 rf(RFM95_CS, RFM95_INT);

void setup() {
    Serial.begin(9600);
    Serial.println("!Booting Receiver");

    pinMode(RFM95_RST, OUTPUT);
    digitalWrite(RFM95_RST, HIGH);
    delay(100);
    digitalWrite(RFM95_RST, LOW);
    delay(10);
    digitalWrite(RFM95_RST, HIGH);
    delay(10);

    if (!rf.init()) {
        Serial.println("!Initialization failed!");
        while (1);
    }

    if (!rf.setFrequency(RF95_FREQ)) {
        Serial.println("!Frequency failed!");
        while (1);
    }

    rf.setTxPower(23, false);
    memset(b64Buf, 0, B64_SIZE + 1);
    Serial.println("!Ready");
}

void loop() {
    uint8_t len = RH_RF95_MAX_MESSAGE_LEN;
    if (rf.available() && rf.recv(binBuf, &len)) {
        encodeBase64(len);
        Serial.println(b64Buf);
    }
}