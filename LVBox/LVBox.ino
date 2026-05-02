#include "packet.h"
#include <Wire.h>

void setup() {
    Serial.begin(9600);
    Serial1.begin(115200);
    Wire.begin();
}
void loop() {}