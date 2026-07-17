/**
Authors:
Natu Benyam Demeke
Violet Enslow
Ryanne Wilson


Precharge Controller - Arduino UNO

Feel free to change any of the output pins!

TODO: Update pins for UNO (check if you need to)

To add:
  - BMS_NMOS_Discharge_Enable
    - output pin
    - input pin (from Feather)
  - BMS_NMOS_Charge_Enable
    - output pin
    - input pin (from Feather)
*/

#define MAX_TIMER 4294967295UL // 4294967295UL Serves as a 'null' state for the timers

// 2 TAKEN
// 3 TAKEN
// 4 TAKEN
// 5 TAKEN
// 6 (ANALOG ONLY)
// 7 (ANALOG ONLY)
// 8 TAKEN
// 9 TAKEN
// 10 TAKEN
// 11 TAKEN
// 12 TAKEN
//
// 13 
// 14 TAKEN
// 15 TAKEN
// 16 TAKEN
// 17 TAKEN
// 18 TAKEN
// 19
//  output pins
#define AIR_Precharge 4
#define AIR_Main 5
#define AIR_Discharge 14
#define BPS_Fault 8
#define LED_Discharge 3
#define LED_Fault 10
#define NMOS_Discharge_En 17 /** Active HIGH */
#define NMOS_Charge_En 18    /** Active HIGH */

// input pins
#define Optocoupler 9 // input_pullup !
#define BMS_DischargeEn 11
#define BMS_MPO 12 // BMS Multi-Purpose Output
#define Feather_BPS_Fault 2
#define Feather_NMOS_Discharge_En 15 /** Active HIGH */
#define Feather_NMOS_Charge_En 16    /** Active HIGH */

bool dischargeEn = false; /** tracks state of NMOS_Discharge_En */
bool chargeEn = false;    /** tracks state of NMOS_Charge_En */

bool carRunning = false;        // True when the car can start driving ; as in, when precharging has finished and is successful.
bool prechargeFailed = false;   // True if the precharge failed.
bool dischargeFinished = false; // True if the discharge finished!

// All measurements of time are in milliseconds!

unsigned long initalizeStart = MAX_TIMER; // Start time for waiting for Discharge Enable signal from BMS
#define initalizeTimeout 5e3              // 0.5s -- amount of time to wait for Discharge Enable to initalize before faulting

unsigned long prechargeStart = MAX_TIMER;            // The time at which precharge started; in millis; MAX_TIMER acts as a 'null' here.
const unsigned long prechargeTimeoutInterval = 10e4; // 10s ---amount of time that has to pass to mean the precharge failed; in millis
#define prechargeInterval 0.5e3                      // 1.5s -- amount of time necessary to precharge; in millis
bool prechargeTimedOut = false;

unsigned long optocouplerActivatedStart = MAX_TIMER; // The time at which Optocoupler was active; in millis

unsigned long dischargeStart = MAX_TIMER;
#define dischargeInterval 7.79e7 // 77.9s; the amount of time it takes to discharge; in millis;

void setup()
{
  // put your setup code here, to run once:

  // output pins
  pinMode(AIR_Precharge, OUTPUT); // Normally open- LOW = open, HIGH = closed
  pinMode(AIR_Main, OUTPUT);      // Normally open
  pinMode(AIR_Discharge, OUTPUT); // Normally closed

  pinMode(BPS_Fault, OUTPUT); // Normally open ??
  digitalWrite(BPS_Fault, LOW);

  pinMode(LED_Fault, OUTPUT);
  pinMode(LED_Discharge, OUTPUT);

  pinMode(NMOS_Charge_En, OUTPUT);
  pinMode(NMOS_Discharge_En, OUTPUT);
  digitalWrite(NMOS_Charge_En, LOW);
  digitalWrite(NMOS_Discharge_En, LOW);

  // input pins
  pinMode(Optocoupler, INPUT_PULLUP); // Uses internal pullup resistors; default HIGH -> active LOW
  pinMode(BMS_MPO, INPUT);            // Behavior depends on BMS settings
  pinMode(BMS_DischargeEn, INPUT);
  pinMode(Feather_BPS_Fault, INPUT);
  pinMode(Feather_NMOS_Charge_En, INPUT);
  pinMode(Feather_NMOS_Discharge_En, INPUT);

  Serial.begin(9600);
  // while(!Serial);  // THIS FOR DEBUGGING. COMMENT OUT FOR ACTUAL USE.
  Serial.println("Serial works!");

  digitalWrite(AIR_Discharge, HIGH);
  Serial.println(digitalRead(BMS_DischargeEn));

  if (digitalRead(BMS_DischargeEn))
  {
    initalizeStart = millis();
    while (millis() - initalizeStart < initalizeTimeout)
    {
      Serial.println("Waiting for BMS Discharge Enable");
      delay(100); // added
    }
  }
  if (digitalRead(BMS_DischargeEn))
  {
    Serial.println("Error: BMS Discharge Enable Timeout");
    precharge_fault();
  }

  Serial.println("End of setup");
}

void precharge()
{
  /**
  Precharge function for the circuit.

  if precharge failed -> deactivates AIR Precharge.
  if Optocoupler sends signal -> if has been precharging for enough time -> start car; deactivate AIR Precharge.
  */

  Serial.print("Optocoupler: ");
  Serial.println(digitalRead(Optocoupler));

  unsigned long now = millis();
  if (digitalRead(Optocoupler) == LOW)
  { // if Optocoupler is active

    // This part waits for a steady signal from the optocoupler,
    // current duration .5s but that's just a guess.
    if (optocouplerActivatedStart == MAX_TIMER)
      optocouplerActivatedStart = now;

    unsigned long chargingInterval = now - optocouplerActivatedStart;
    Serial.println("Optocoupler Waiting");
    Serial.println(prechargeInterval);
    Serial.println(chargingInterval);

    if (chargingInterval > prechargeInterval)
    {
      carRunning = true;
      Serial.println("Pre-Charge Complete");
      digitalWrite(AIR_Main, HIGH);
      delay(500);
      digitalWrite(AIR_Precharge, LOW);
    }
  }

  // timeout check
  unsigned long timeoutInterval = now - prechargeStart;
  if (timeoutInterval > prechargeTimeoutInterval)
  {
    // Timed out; precharge has failed! fault :(
    prechargeFailed = true;
    digitalWrite(AIR_Precharge, LOW);
    digitalWrite(AIR_Main, LOW);
    digitalWrite(LED_Fault, HIGH);
    prechargeTimedOut = true;
    precharge_fault();
  }
}

void discharge()
{
  digitalWrite(AIR_Discharge, HIGH);
  unsigned long now = millis();
  if (now - dischargeStart > dischargeInterval)
  {
    digitalWrite(LED_Discharge, HIGH);
    dischargeFinished = true;
  }
}

void precharge_fault()
{
  digitalWrite(AIR_Main, LOW);
  digitalWrite(AIR_Discharge, HIGH);
  Serial.println("Pre-Charge Fault");
  while (1)
    ;
}

void bps_fault()
{
  digitalWrite(BPS_Fault, HIGH);
  digitalWrite(NMOS_Charge_En, LOW);
  digitalWrite(NMOS_Discharge_En, LOW);
  Serial.println("BPS Fault");
  while (1)
    ;
}

void loop()
{
  // put your main code here, to run repeatedly:

  // NMOS_Charge_En
  if (!chargeEn && digitalRead(Feather_NMOS_Charge_En))
  {
    digitalWrite(NMOS_Charge_En, HIGH);
    chargeEn = true;
  }
  if (chargeEn && !digitalRead(Feather_NMOS_Charge_En))
  {
    digitalWrite(NMOS_Charge_En, LOW);
    chargeEn = false;
  }

  // NMOS_Discharge_En
  if (!dischargeEn && digitalRead(Feather_NMOS_Discharge_En))
  {
    digitalWrite(NMOS_Discharge_En, HIGH);
    dischargeEn = true;
  }
  if (dischargeEn && !digitalRead(Feather_NMOS_Discharge_En))
  {
    digitalWrite(NMOS_Discharge_En, LOW);
    dischargeEn = false;
  }

  // Precharge Fault
  if (digitalRead(BMS_DischargeEn) == HIGH || prechargeTimedOut == true)
  {
    precharge_fault();
  }

  if (digitalRead(BMS_MPO) == HIGH || digitalRead(Feather_BPS_Fault) == HIGH)
  {
    bps_fault();
  }
  else
  {
    digitalWrite(BPS_Fault, LOW);
  }

  if (carRunning == false)
  {
    if (digitalRead(BMS_DischargeEn) == LOW)
    { //&& digitalRead(BMS) == HIGH
      if (prechargeStart == MAX_TIMER)
      {                                    // if the prechargeStart hasn't yet been assigned
        digitalWrite(AIR_Precharge, HIGH); // Closes AIR precharge
        prechargeStart = millis();
      }
      Serial.println("Pre-Charging");
      precharge();
      Serial.println("Pre-Charging");
    }
  }
}
