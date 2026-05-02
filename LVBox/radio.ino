#include "radio.h"
#include "packet.h"
#include <SPI.h>
#include <RH_RF95.h>

#define RFM95_CS   8
#define RFM95_RST  4
#define RFM95_INT  3
#define RF95_FREQ 915.0
#define MAX_FAILS 100

RH_RF95 rf(RFM95_CS, RFM95_INT);
int radio_failed = 1;

/// Initialize the radio
void radio_init() {
    pinMode(RFM95_RST, OUTPUT);
    digitalWrite(RFM95_RST, HIGH);
    delay(100);
    digitalWrite(RFM95_RST, LOW);
    delay(10);
    digitalWrite(RFM95_RST, HIGH);
    delay(10);
    int fails = 0;
    while (fails < 100 && !rf.init()) {
        Serial.println("!Initialization failed");
        delay(10);
        ++fails;
    }
    while (fails < 100 && !rf.setFrequency(RF95_FREQ)) {
        Serial.println("!Freuency failed");
        delay(10);
        ++fails;
    }
    radio_failed = 0;
}
/// Send the data in the global packet over LoRa
void radio_send() {
    if (radio_failed) return;
    rf.send((uint8_t*)(&packet), sizeof(packet_t)); // cast the packet data to bytes and send it
}