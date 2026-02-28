/*
  CAN receiver!
*/

#include <CANSAME5x.h>

CANSAME5x CAN;

void setup(){
  Serial.begin(115200);
  while(!Serial) delay(10);

  Serial.println("CAN Receiver");

  pinMode(PIN_CAN_STANDBY, OUTPUT);
  digitalWrite(PIN_CAN_STANDBY, false);;
}