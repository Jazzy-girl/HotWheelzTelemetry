#include <Adafruit_GPS.h>
#define GPSSerial Serial1

float gps_longitude;
float gps_latitude;
float gps_speed;

Adafruit_GPS GPS(&GPSSerial);

#define INIT_COMMAND_1 "$PMTK314,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28"
#define INIT_COMMAND_2 "$PMTK220,500*2B"

bool gps_check_connection(unsigned long timeout_ms = 3000) {
    unsigned long start = millis();
    while (millis() - start < timeout_ms) {
        while (GPSSerial.available()) { // Are there any bytes already waiting in the buffer?
            char c = GPS.read();
            if (c) Serial.print(c); // Print raw NMEA data for debugging
            // If nothing prints, the GPS isn’t talking.
        }

        if (GPS.newNMEAreceived()) {    // Check if we received a new NMEA sentence
            if (GPS.parse(GPS.lastNMEA())) {    // Try to parse it, if it’s valid, we have a connection
                Serial.println("GPS connection OK");
                return true;
            }
        }
    }

    Serial.println("GPS connection check failed: no valid NMEA data received");
    return false;
}

void gps_init() {
    GPSSerial.begin(9600);

    GPS.sendCommand(INIT_COMMAND_1);
    GPS.sendCommand(INIT_COMMAND_2);

    GPSSerial.println(PMTK_Q_RELEASE);

    gps_check_connection();
}

void gps_poll() {
    while (GPSSerial.available()) {
        char c = GPS.read();
        if (c) Serial.print(c);
    }

    if (GPS.newNMEAreceived()) {
        if (!GPS.parse(GPS.lastNMEA()))
            return;
    }

    Serial.print("Fix: "); Serial.println(GPS.fix);
    Serial.print("Quality: "); Serial.println(GPS.fixquality);
    Serial.print("Satellites: "); Serial.println(GPS.satellites);

    if (GPS.fix) {
        gps_latitude = GPS.latitudeDegrees;
        gps_longitude = GPS.longitudeDegrees;
        gps_speed = GPS.speed * 1.852f;

        Serial.print("Lat: "); Serial.println(gps_latitude, 6);
        Serial.print("Lon: "); Serial.println(gps_longitude, 6);
        Serial.print("Speed: "); Serial.println(gps_speed);
    } else {
        Serial.println("No GPS fix yet...");
    }
}