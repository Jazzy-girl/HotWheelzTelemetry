// #define NMEA_FLOAT_T double
#include <Adafruit_GPS.h>
#define GPSSerial Serial1

#define TX (0)
#define RX (1)

float gps_longitude;
float gps_latitude;
float gps_speed;

Adafruit_GPS GPS(&GPSSerial);

#define command ("PMTK314,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
#define command2 ("PMTK220,500")

void gps_init()
{
    // probably don't need to config pins!
    GPSSerial.begin(9600);

    // GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
    GPS.sendCommand(command);
    GPS.sendCommand(command2);
    // Set the update rate
    // GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ); // 1 Hz update rate

    // // Request updates on antenna status, comment out to keep quiet
    // GPS.sendCommand(PGCMD_ANTENNA);

    // Ask for firmware version
    GPSSerial.println(PMTK_Q_RELEASE);
}

/// retu
void gps_poll()
{
    char c = GPS.read();
    if (GPS.newNMEAreceived())
    {
        if (!GPS.parse(GPS.lastNMEA())) // this also sets the newNMEAreceived() flag to false
            return;                     // we can fail to parse a sentence in which case we should just wait for another
    }

    gps_latitude = GPS.latitude;
    gps_longitude = GPS.longitude;
    gps_speed = GPS.speed;
}