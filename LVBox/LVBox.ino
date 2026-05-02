#include "packet.h"
#include "motor.h"
#include <Wire.h>

packet_t packet;

void setup() {
    Serial.begin(9600);
    Serial1.begin(9600);
    Wire.begin();
    motor_controller_init();
}
void loop() {
    motor_controller_poll();
}