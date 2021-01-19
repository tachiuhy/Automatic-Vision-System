#include <PWM.h>
#include <Wire.h>

int ir_pin1 = 2;
bool hitObject1 = false;
int counter1 = 0;
int condition = 0;

const int list_num = 6;
int list[list_num];
int list_index = 0;

void setup() {
  Serial.begin(9600);
  Wire.begin(); 
  pinMode(ir_pin1, INPUT);


  InitTimersSafe();
  pinMode(9, OUTPUT);
  SetPinFrequencySafe(9, 2500);
  
  for ( int i = 0; i < list_num; i++){
    list[i] = 0;
  }
}

void loop() {
  while (condition == 0) {
    if (Serial.available() ){
      
      if (Serial.readStringUntil('\n') == "Start" ) {
        condition = 1;
        pwmWrite(9, 127);
      }}
    else {
      condition = 0;
    }}


  while (condition == 1) {

//Counter1________________________________________________________
  int val1 = (digitalRead(ir_pin1));
  if ((val1 == 0) && (hitObject1 == false) ) {
    counter1++;
    hitObject1 = true;
  }
  else if ( (val1 == 1) && (hitObject1 == true) ) {
    hitObject1 = false;
  }
  delay(5);

  
//BottleList_&_Stop_Program_________________________________________________
  if (Serial.available()) {
      String pos = Serial.readStringUntil('\n');
      if (pos == "Stop") {
      condition = 0;
      counter1 = 0;
      pwmWrite(9, 0);
      Wire.beginTransmission(9);
      Wire.write(0);
      Wire.endTransmission(); 
      
    }
  else {
    condition = 1;
    byte(pos);
    Wire.beginTransmission(9);
    Wire.write(pos);
    Wire.endTransmission(); 
    Wire.requestFrom(9, 1);    
    if(Wire.available()) { 
      byte i2c_rcv;   
      i2c_rcv = Wire.read();
    } 
  }}
  
}}
