#include "packet.h"
#include "motor.h"
#include "radio.h"
#include "gps.h"
#include <Wire.h>

#define THERMISTOR_INPUT A0

void setup() {
    Serial.begin(9600);
    Wire.begin();
    motor_controller_init();
    radio_init();
    gps_init();
    packet.H = 'H';
    packet.W = 'W';
}

void loop() {
    motor_controller_poll();
    gps_poll();
    packet.timestamp = millis();
    packet.motor_speed = motor_controller_pulses();
    packet.longitude = gps_longitude;
    packet.latitude = gps_latitude;
    packet.gps_speed = gps_speed;
    packet.cockpit_temp = analogRead(THERMISTOR_INPUT);
    swap_packet_bytes(&packet);
    write_checksum(&packet);
    radio_send();
}