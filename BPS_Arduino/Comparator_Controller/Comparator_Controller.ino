#define OPTO_OUT 2
#define PRE_RESISTOR A0
#define POST_RESISTOR A1

void setup(){
  pinMode(OPTO_OUT, OUTPUT);
  digitalWrite(OPTO_OUT, LOW);
}

void loop (){
  digitalWrite(OPTO_OUT, analogRead(PRE_RESISTOR) < analogRead(POST_RESISTOR) ? LOW : HIGH);
}