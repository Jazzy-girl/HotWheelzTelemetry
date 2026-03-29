/**
Authors:
Natu Benyam Demeke
Violet Enslow
Ryanne Wilson


Precharge Controller
No comparator; instead, when switch 2 is flipped, closes the Precharge AIR for 7 seconds before opening it and then closing the Main AIR.
*/

#define ULONG_MAX 4294967295UL //Serves as a 'null' state for the timers

//pin IDs
const uint8_t AIR_Precharge = 5; 
const uint8_t AIR_Main = 7;

bool carRunning = false; //True when the car can start driving ; as in, when precharging has finished and is successful.
bool prechargeFailed = false; //True if the precharge failed.
bool dischargeFinished = false; // True if the discharge finished!

//All measurements of time are in milliseconds!

unsigned long prechargeStart = ULONG_MAX; // The time at which precharge started; in millis; ULONG_MAX acts as a 'null' here.
const unsigned long prechargeTimeoutInterval = 10e4; // 10s ---amount of time that has to pass to mean the precharge failed; in millis
const unsigned long prechargeInterval = 7000; // 7s -- amount of time necessary to precharge; in millis

unsigned long optocouplerActivatedStart = ULONG_MAX; // The time at which Optocoupler was active; in millis

unsigned long dischargeStart = ULONG_MAX;
const unsigned long dischargeInterval = 7.79e7; // 77.9s; the amount of time it takes to discharge; in millis;

void setup() {
  // put your setup code here, to run once:
  pinMode(AIR_Precharge, OUTPUT);     // Normally open- LOW = open, HIGH = closed
  pinMode(AIR_Main, OUTPUT);          // Normally open
  pinMode(13, OUTPUT);
}

void precharge() {

    unsigned long now = millis();
    
    if (now - prechargeStart > prechargeInterval) { //If it has been 7 seconds
      //Sets the car running; opens the precharge AIR, closes the main AIR
      carRunning = true;
      digitalWrite(AIR_Precharge, LOW);
      digitalWrite(AIR_Main, HIGH);
      digitalWrite(13, HIGH);
    }

}

void loop() {
  // put your main code here, to run repeatedly:
  if (carRunning == false) {
        if (prechargeStart == ULONG_MAX) {   //if the prechargeStart hasn't yet been assigned         
            digitalWrite(AIR_Precharge, HIGH); //Closes AIR precharge
            digitalWrite(AIR_Main, LOW);
            prechargeStart = millis();
            }
        precharge();
  }
}

