/**
 * Author: Ryanne Wilson
 * BPS Arduino for Props.
 * 
 */

// INCLUDE

#include <Arduino_CAN.h>

const int HITEMP_INDEX = 8;
const int OFFSET = -40;

void setup(){
  Serial.begin(115200)
  while(!Serial);

  if(!CAN.begin(CanBitRate::BR_250k)){
    Serial.println("CAN.begin(...) failed.");
    for(;;) {}
  }
}

// If MPS is HIGH or Hitemp >= 55, Fault (HIGH; 5V) else output LOW; 0V

void loop(){
  if(CAN.available()){
    CanMsg const msg = CAN.read();
    Serial.println(msg);
    int idMessage = msg.getStandardid();
    Serial.print("IDMessage= ");
    Serial.println(idMessage);

    // offset -40
    int temp = msg.data[HITEMP_INDEX];
    temp -= OFFSET;

    if (temp >= 55){
      // Send out a fault!
    }
    
  }
}