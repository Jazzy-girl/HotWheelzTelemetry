#ifndef MOTOR_H
#define MOTOR_H

#include <stdint.h>

/// Initialize the motor controller interface
void motor_controller_init();
/// Poll for pulse state changes at the start of a loop
void motor_controller_poll();
/// Get the number of pulses in the last second
uint16_t motor_controller_pulses();

#endif // MOTOR_H