#include <Wire.h>

#define ADDRESS 0x52

// data to send over I2C
byte data[] = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24 };

void setup() {
  Serial.begin(9600);
  // while (!Serial) delay(10);
  Wire.begin(ADDRESS);
  Wire.onRequest(requestEvent);
  Wire.onReceive(receiveEvent);
  Serial.println("Starting");
}
void loop() {}
void requestEvent() {
  Serial.println("Request!");
  Wire.write(data, 24);
}
void receiveEvent() {
  Serial.print("Receive: ");
  while (Wire.available()) {
    Serial.write(Wire.read());
  }
  Serial.println();
}
