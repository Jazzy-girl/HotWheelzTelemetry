// change this if we wire it differently
#define RFM95_CS   8
#define RFM95_RST  4
#define RFM95_INT  3

#include "common.h"

void setup() {
    while (!Serial);
    Serial.begin(9600);
    Serial.println("Starting PING board");

    initRadio();
}

void loop() {
    char fmtBuf[PAYLOAD_LEN + 1];
    fmtBuf[PAYLOAD_LEN] = 0;

    long fmtStart = micros();
    memcpy(buf, BASE_PING, PREFIX_LEN);
    short tmp = COUNTER++;
    char* bStart = buf + MESSAGE_LEN;
    char* bEnd = buf + PREFIX_LEN;
    while (bStart-- > bEnd) {
        *bStart = HEX_BYTES[tmp & 15];
        tmp >>= 4;
    }
    memcpy(fmtBuf, buf + PREFIX_LEN, PAYLOAD_LEN);
    buf[MESSAGE_LEN] = 0;
    long fmtEnd = micros();

    Serial.print("Message: ");
    Serial.println(buf);

    Serial.print("Formatted in ");
    Serial.print(fmtEnd - fmtStart);
    Serial.println("us");

    long sendStart = micros();
    rf.send((uint8_t*)buf, MESSAGE_LEN);
    // rf.waitPacketSent();
    long sendEnd = micros();

    Serial.print("Sent in ");
    Serial.print(sendEnd - sendStart);
    Serial.println("us");

    long listenStart = micros();
    long deadline = listenStart + 10000000;
    long currentRx;
    int received = 0;
    bool valid = false;
    do {
        currentRx = micros();
        uint8_t len = RH_RF95_MAX_MESSAGE_LEN;
        if (rf.available() && rf.recv((uint8_t*)buf, &len)) {
            ++received;
            if (len == MESSAGE_LEN && !memcmp(buf, BASE_PONG, PREFIX_LEN)) {
                // we're receiving a pong
                if (memcmp(buf + PREFIX_LEN, fmtBuf, PAYLOAD_LEN)) {
                    Serial.print("Got a packet with the wrong payload: expected ");
                    Serial.print(fmtBuf);
                    Serial.print(", got ");
                    Serial.println(buf + PREFIX_LEN);
                } else {
                    valid = true;
                    Serial.println("Received matching pong");
                    break;
                }
            } else {
                printUnexpected(len);
            }
        }
    } while (currentRx < deadline); // 10s timeout
    
    Serial.print("Listened for ");
    Serial.print(currentRx - listenStart);
    Serial.println("us");
    Serial.print("Received ");
    Serial.print(received);
    Serial.println(valid ? " messages, with valid" : " messages, none valid");
}