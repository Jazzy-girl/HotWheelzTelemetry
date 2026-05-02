#include "motor.h"

#define MOTOR_CONTROLLER_PIN 3
#define MAX_PULSES 1024
#define PULSE_MASK (MAX_PULSES - 1)
#define SECOND 1000000

int lastVal;

/// Start index of the ring buffer
int rb_start = 0;
/// End index of the ring buffer
int rb_end = 0;

long pulse_times[MAX_PULSES];

/// Initialize the motor controller interface
void motor_controller_init() {
    pinMode(MOTOR_CONTROLLER_PIN, INPUT);
    lastVal = digitalRead(MOTOR_CONTROLLER_PIN);
}
/// Poll for pulse state changes at the start of a loop
void motor_controller_poll() {
    int newVal = digitalRead(MOTOR_CONTROLLER_PIN);
    long now = micros();
    if (newVal != lastVal) {
        lastVal = newVal;
        if (newVal) {
            pulse_times[rb_end] = now;
            rb_end = (rb_end + 1) & PULSE_MASK; // add one, wrap around
            rb_start = (rb_start + (rb_start == rb_end)) & PULSE_MASK; // if rb_start == rb_end, increment rb_start
        }
    }
    long min = now - SECOND;
    if (min < 0) return;
    while (rb_start != rb_end) {
        if (pulse_times[rb_start] < min) ++rb_start;
        else return;
    }
}
/// Get the number of pulses in the last second
uint16_t motor_controller_pulses() {
    return (rb_end - rb_start) & PULSE_MASK;
}