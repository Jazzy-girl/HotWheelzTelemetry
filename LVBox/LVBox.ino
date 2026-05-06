#include "packet.h"
#include "motor.h"
#include "radio.h"
#include "GPS.h"
#include "BMS.h"
#include "USB.h"

#define THERMISTOR_INPUT A1
#define SEND_INTERVAL 500 // ms

long send_ts;

void setup() {
    motor_controller_init();
    radio_init();
    gps_init();
    bms_init();
    serial_init();
    send_ts = millis() + SEND_INTERVAL;
    PACKET.H = 'H';
    PACKET.W = 'W';
}

void loop() {
    motor_controller_poll();
    long now = millis();
    if (now < send_ts) return;
    send_ts = now + SEND_INTERVAL;
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
    send_serial();
}
