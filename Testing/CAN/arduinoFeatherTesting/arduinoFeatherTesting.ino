/*
  CAN receiver!
*/

#include <CANSAME5x.h>

CANSAME5x CAN;

void setup(){
  Serial.begin(115200);
  // Serial.begin(9600);
  while(!Serial) delay(10);

  Serial.println("CAN Receiver");

  pinMode(PIN_CAN_STANDBY, OUTPUT);
  digitalWrite(PIN_CAN_STANDBY, LOW);; // turn off STANDBY
  pinMode(PIN_CAN_BOOSTEN, OUTPUT);
  digitalWrite(PIN_CAN_BOOSTEN, true); // turn on booster

  // start the CAN bus at 250 kbps
  int buadrate = 250000;
  if(!CAN.begin(buadrate)){ // 5000000
    Serial.println("Starting CAN failed!");
    while (1) delay(10);
  }
  Serial.println("Starting CAN!");
}

void loop() {
  int packetSize = CAN.parsePacket();
  if(packetSize){
    // received a packet!
    Serial.print("Received ");

    if(CAN.packetExtended()){
      Serial.print("extended ");
    }

    if(CAN.packetRtr()){
      // Remote transmission request, packet contains no data
      Serial.print("RTR ");
    }

    Serial.print("packet with id 0x");
    Serial.print(CAN.packetId(), HEX);

    if(CAN.packetRtr()){
      Serial.print(" and requestd length ");
      Serial.println(CAN.packetDlc());
    }else{
      Serial.print(" and length ");
      Serial.println(packetSize);

      // only print packet data for non-RTR packets
      while(CAN.available()){
        Serial.print((char)CAN.read());
      }
      Serial.println();
    }
    Serial.println();
  }
}