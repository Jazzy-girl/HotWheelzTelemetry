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

Output to MPS Safety Circuit (via UNO intermediary):
  Look at MPO and CAN Bus Data
  If MPO is High OR CAN Bus Highest Temperature Attribute is >= 55 C, output High (5 V)
  Otherwise, output Low (0V)

  If the CANbus never initializes, also causes a fault.

TODO:
OUTPUT -- BMS_NMOS_discharge_enable (new output)
  Active HIGH if:
    highest voltage cell <= 4.2V
    && lowest voltage cell > 2.5V
    && -12 A <= current <= 45 A
    && highest temperature cell <= 55 C
    && no BPS fault

OUTPUT -- BMS_NMOS_charge enable (new output)
  Active HIGH if:
    If highest voltage cell < 4.2V
    && lowest voltage cell >= 2.5V
    && -12 A <= current <= 45 A
    && highest temperature cell <= 55 C
    && no BPS fault

OUTPUT -- BPS_Fault (rewrite existing output logic)
  Active HIGH if:
    Highest voltage cell > 4.2V
    || lowest voltage cell < 2.5V
    || current > 45 A
    || current < -12 A
    || highest temperature cell > 55 C
  once HIGH, can not go low

  HOW TO EDIT THIS :
    Change the #define BPS_Fault pin to the GPIO pin you want that will send out a 3.3v HIGH signal when CANbus data shows Thermistor is too hot.
    Change the bitrate if you edit the BMS's kbps settings.


*/

#include <CANSAME5x.h>
#include <Wire.h>

CANSAME5x CAN;

// Output pins
#define BPS_Fault 5                             /** Active HIGH */
#define BMS_NMOS_discharge_enable 0xPLACEHOLDER /** Active HIGH */
#define BMS_NMOS_charge_enable 0xPLACEHOLDER    /** Active HIGH */

bool dischargeEnable = false;
bool chargeEnable = false;
bool BPSFaulted = false;
#define PLACEHOLDER = 999999;
int highCellVolt = PLACEHOLDER;
int lowCellVolt = PLACEHOLDER;
int current = 0;
int highTemp = 0;

#define bitrate 500000 // 500 kbps

// CANbus constants
#define ID1 0x001
#define ID2 0x002
#define ID3 0x003
#define LOWER_ID_Bound 0x000  // exlusive
#define HIGHER_ID_Bound 0x004 // exclusive

#define HITEMP_INDEX {2} // Index of High Temprature in CAN message
#define HIVOLT_INDICES {4, 5}
#define LOVOLT_INDICES {6, 7}
#define CURRENT_INDICES {4, 5}

#define HITEMP_BOUND 55
#define HIVOLT_BOUND 42000
#define LOVOLT_BOUND 25000 
#define CURRENT_LOWERBOUND -12
#define CURRENT_UPPERBOUND 45

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

  // BPS Fault -> Output to UNO
  pinMode(BPS_Fault, OUTPUT);
  digitalWrite(BPS_Fault, LOW);

  // BMS_NMOS_discharge_enable
  pinMode(BMS_NMOS_discharge_enable, OUTPUT);
  digitalWrite(BMS_NMOS_discharge_enable, LOW);
  pinMode(BMS_NMOS_charge_enable, OUTPUT);
  digitalWrite(BMS_NMOS_charge_enable, LOW);

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

int getIndex(int msgID, int index)
{
  return (msgID - 1) * 8 + index;
}

int getMultiByteBigEndianValue(int msgID, int numBytes, int[] indices)
{
  int value = 0;
  for (int i = 0; i < numBytes; i++)
  {
    value << 8;
    int index = getIndex(msgID, indices[i]);
    value += messages[index];
  }
  return value;
}

void readCAN()
{
  int packetSize = CAN.parsePacket();

  // Serial.println("CAN!");
  if (packetSize)
  {
    long packetID = CAN.packetId();

    if (packetID > LOWER_ID_Bound && packetID < HIGHER_ID_Bound)
    {

      // iterate through
      int i = (packetID - 1) * 8;
      int end = i + 8;
      for (; i < end; ++i)
      { // IDs are 1, 2, 3
        messages[i] = CAN.read();
      }

      switch (packetID)
      {
      case ID1:
        current = getMultiByteBigEndianValue(ID1, 2, CURRENT_INDICES);
        break;
      case ID2:
        highCellVolt = getMultiByteBigEndianValue(ID2, 2, HIVOLT_INDICES);
        lowCellVolt = getMultiByteBigEndianValue(ID2, 2, LOVOLT_INDICES);
        break;
      case ID3:
        highTemp = getMultiByteBigEndianValue(ID3, 1, HITEMP_INDEX);
        break;
      default:
        break;
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
  digitalWrite(BMS_NMOS_charge_enable, LOW);
  digitalWrite(BMS_NMOS_discharge_enable, LOW);
  BPSFaulted = true;
}

void updateOutputs()
{
  // If the BPS Faults, then everything should stay LOW.
  if(BPSFaulted){
    return;
  }

  if (highCellVolt != PLACEHOLDER && lowCellVolt != PLACEHOLDER)
  {

    // check for NMOS discharge
    if (highCellVolt <= HIVOLT_BOUND && lowCellVolt > LOVOLT_BOUND && current >= CURRENT_LOWERBOUND && current <= CURRENT_UPPERBOUND && highTemp <= HITEMP_BOUND)
    {
      if (!dischargeEnable)
      {
        digitalWrite(BMS_NMOS_discharge_enable, HIGH);
        dischargeEnable = true;
      }
    }
    else
    {
      if (dischargeEnable)
      {
        digitalWrite(BMS_NMOS_discharge_enable, LOW);
        dischargeEnable = false;
      }
    }

    // check for NMOS charge
    if (highCellVolt < HIVOLT_BOUND && lowCellVolt >= LOVOLT_BOUND && current >= CURRENT_LOWERBOUND && current <= CURRENT_UPPERBOUND && highTemp <= HITEMP_BOUND)
    {
      if (!chargeEnable)
      {
        digitalWrite(BMS_NMOS_charge_enable, HIGH);
        chargeEnable = true;
      }
    }
    else
    {
      if (chargeEnable)
      {
        digitalWrite(BMS_NMOS_charge_enable, LOW);
        chargeEnable = false;
      }
    }
  }

  // check for BPS fault
  if (highCellVolt > HIVOLT_BOUND && highCellVolt != PLACEHOLDER)
  {
    fault();
  }
  if (lowCellVolt < LOVOLT_BOUND && lowCellVolt != PLACEHOLDER)
  {
    fault();
  }
  if (current < CURRENT_LOWERBOUND || current > CURRENT_UPPERBOUND ||
      highTemp > HITEMP_BOUND)
  {
    fault();
  }
}

void loop()
{
  // put your main code here, to run repeatedly:

  readCAN();
  updateOutputs();
}
