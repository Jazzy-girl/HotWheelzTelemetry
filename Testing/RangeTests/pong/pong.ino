// change this if we wire it differently
#define RFM95_CS   8
#define RFM95_RST  4
#define RFM95_INT  3

#include "common.h"

void setup() {
    while (!Serial);
    Serial.begin(9600);
    Serial.println("Starting PONG board");

    initRadio();
}
void loop() {
    uint8_t len = RH_RF95_MAX_MESSAGE_LEN;
    if (rf.available() && rf.recv((uint8_t*)buf, &len)) {
        if (len == MESSAGE_LEN && !memcmp(buf, BASE_PING, PREFIX_LEN)) {
            buf[1] = 'O'; // change the PING to PONG

            long sendStart = micros();
            rf.send((uint8_t*)buf, MESSAGE_LEN);
            rf.waitPacketSent();
            long sendEnd = micros();

            Serial.print("Sent in ");
            Serial.print(sendEnd - sendStart);
            Serial.println("us");
        } else {
            printUnexpected(len);
        }
    }
}