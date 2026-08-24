#ifndef GPS_H
#define GPS_H
#include <stdint.h>
#include "packet.h"

extern float gps_longitude;
extern float gps_latitude;
extern float gps_speed;

/// Initialize the GPS
void gps_init();
/// Update the GPS to get new data
void gps_poll();

#endif