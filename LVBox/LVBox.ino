#include "packet.h"
#include "motor.h"
#include "radio.h"
#include <Wire.h>

void setup() {
    Serial.begin(9600);
    Serial1.begin(9600);
    Wire.begin();
    motor_controller_init();
    radio_init();
    packet.H = 'H';
    packet.W = 'W';
}

void loop() {
    motor_controller_poll();
    packet.timestamp = millis();
    packet.motor_speed = motor_controller_pulses();
    swap_packet_bytes(&packet);
    write_checksum(&packet);
    radio_send();
}