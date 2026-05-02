#include "packet.h"
#include "motor.h"
#include "radio.h"
#include "GPS.h"
#include "BMS.h"

#define THERMISTOR_INPUT A0

void setup() {
    Serial.begin(9600);
    motor_controller_init();
    radio_init();
    gps_init();
    bms_init();
    PACKET.H = 'H';
    PACKET.W = 'W';
}

void loop() {
    motor_controller_poll();
    gps_poll();
    bms_poll();
    PACKET.timestamp = millis();
    PACKET.motor_speed = motor_controller_pulses();
    PACKET.longitude = gps_longitude;
    PACKET.latitude = gps_latitude;
    PACKET.gps_speed = gps_speed;
    PACKET.cockpit_temp = analogRead(THERMISTOR_INPUT);
    swap_packet_bytes();
    write_checksum();
    radio_send();
}