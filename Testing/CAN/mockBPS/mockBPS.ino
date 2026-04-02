#include <Wire.h>

#define ADDRESS 0x52

// data to send over I2C
byte data[] = {81, 0, 0, 0, 30, 0, 16, 39, 26, 39, 38, 2, 5, 0, 1, 0, 111, 11, 210, 21, 99, 9, 120, 4, 7};

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
  Wire.write(data, 25);
}
void receiveEvent(int) {
  Serial.print("Receive: ");
  while (Wire.available()) {
    Serial.write(Wire.read());
  }
  Serial.println();
}
