#ifndef GPS_H
#define GPS_H
#include <stdint.h>

extern double gps_longitude;
extern double gps_latitude;
extern float gps_speed;

void gps_init();

void gps_poll();

#endif