/**
Authors:
Natu Benyam Demeke
Ryanne Wilson


BPS Controller - Arduino Feather M4 CAN

Sends CAN messages over I2C. LSB of last byte (25th byte) is parity bit. Uses even parity, so there should be an even number of 1s.

Inputs from BMS :
  Multi-Purpose Output (MPO)
  High (5 V) = BPS Fault
  Low (0 V) = BPS OK
  CAN Bus
  Read CANBUS thermistor data, should be able to have the highest temperature in the data package

Output to MPS Safety Circuit (via Nano intermediary):
  Look at MPO and CAN Bus Data
  If MPO is High OR CAN Bus Highest Temperature Attribute is >= 55 C, output High (5 V)
  Otherwise, output Low (0V)

  If the CANbus never initializes, also causes a fault.


  HOW TO EDIT THIS :
    Change the #define BPS_Fault pin to the GPIO pin you want that will send out a 3.3v HIGH signal when CANbus data shows Thermistor is too hot.
    Change the bitrate if you edit the BMS's kbps settings.
*/

#include <CANSAME5x.h>
#include <Wire.h>

CANSAME5x CAN;

// Output pins
#define BPS_Fault 6 /**  */

#define bitrate 500000 // 500 kbps

// CANbus constants
#define correctID 0x003
#define HITEMP_INDEX 2 // Index of High Temprature in CAN message
#define OFFSET -40

// If MPS is HIGH or Hitemp >= 55, Fault (HIGH; 5V) else output LOW; 0V

// I2C
#define address 0x52
#define messages_length 25
unsigned char messages[messages_length];

// parity lookup table (0 = even, 1 = odd)
const byte lookup[] =
    {0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0,
     1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0,
     1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1,
     1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1,
     0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1,
     0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0,
     1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0};

void setup()
{
  // put your setup code here, to run once:

  // BPS Fault -> Output to Nano
  pinMode(BPS_Fault, OUTPUT);
  digitalWrite(BPS_Fault, LOW);

  // CANbus pins
  pinMode(PIN_CAN_STANDBY, OUTPUT);
  digitalWrite(PIN_CAN_STANDBY, LOW); // turn off STANDBY; also try: false
  pinMode(PIN_CAN_BOOSTEN, OUTPUT);
  digitalWrite(PIN_CAN_BOOSTEN, HIGH); // turn on booster; also try: true

  Serial.begin(115200);
  // while(!Serial);  // THIS FOR DEBUGGING. TURN OFF FOR ACTUAL USE.

  if (!CAN.begin(bitrate))
  { // Fault if CAN begin fails?
    Serial.println("CAN.begin(...) failed.");
    fault();
  }

  Wire.begin(address);
  Wire.onRequest(sendBuffered); // event for I2C requests

  Serial.println("End of setup");
}

void readCAN()
{
  int packetSize = CAN.parsePacket();

  // Serial.println("CAN!");
  if (packetSize)
  {
    long packetID = CAN.packetId();
    if (packetID > 0 && packetID < 4)
    {

      int i = (packetID - 1) * 8;
      int end = i + 8;
      for (; i < end; ++i)
      { // IDs are 1, 2, 3
        messages[i] = CAN.read();
      }

      if (packetID == correctID)
      {
        int tempindex = (correctID - 1) * 8 + HITEMP_INDEX;
        int temp = messages[tempindex];
        Serial.print("TEMP: ");
        Serial.println(temp);

        if (temp >= 55)
        {
          fault();
        }
      }
      unsigned char idCheck = (1 << packetID);
      messages[24] = messages[24] | idCheck;
    }

    while (CAN.available())
    {
      CAN.read();
    }

    // DEBUGGING CAN MESSAGES
    // if (packetSize >= 3) {
    //   Serial.print("Received packet with id ");
    //   long packetID = CAN.packetId();
    //   Serial.println(packetID);
    //   Serial.println(packetID, HEX);
    //   for(int i = 0; i < packetSize; i++){
    //     Serial.print("field ");
    //     Serial.print(i);
    //     Serial.print(": ");
    //     Serial.println(CAN.read());
    //    }
    // }
  }
  delay(500);
}

void sendBuffered()
{
  byte checksum = 0;
  messages[24] &= 0xFE; // clear the LSB of the last byte!
  for (int i = 0; i < messages_length; ++i)
  {
    checksum ^= lookup[messages[i]];
  }
  messages[24] |= checksum; // make LSB of last byte 1 or 0 to ensure even number of 1s.
  Wire.write(messages, messages_length);
  messages[24] = 0; // set back to 0.
}

void fault()
{
  digitalWrite(BPS_Fault, HIGH);
  while (1)
    ;
}

void loop()
{
  // put your main code here, to run repeatedly:

  readCAN();
}
