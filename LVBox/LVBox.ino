#include "packet.h"
#include "motor.h"
#include "radio.h"
#include "GPS.h"
#include "BMS.h"
#include "USB.h"

#define THERMISTOR_INPUT A1
#define SEND_INTERVAL 500 // ms

#ifdef __arm__
// should use uinstd.h to define sbrk but Due causes a conflict
extern "C" char* sbrk(int incr);
#else  // __ARM__
extern char *__brkval;
#endif  // __arm__

int freeMemory() {
  char top;
#ifdef __arm__
  return &top - reinterpret_cast<char*>(sbrk(0));
#elif defined(CORE_TEENSY) || (ARDUINO > 103 && ARDUINO != 151)
  return &top - __brkval;
#else  // __arm__
  return __brkval ? &top - __brkval : &top - __malloc_heap_start;
#endif  // __arm__
}

long send_ts;



void setup() {
    while (!Serial);
    motor_controller_init();
    radio_init();
    gps_init();
    bms_init();
    serial_init();
    send_ts = millis() + SEND_INTERVAL;
    PACKET.H = 'H';
    PACKET.W = 'W';
    Serial.println("!Initialization complete");
    freeMemory();
}

void loop() {
    freeMemory();
    // Serial.println("start of loop!");
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
