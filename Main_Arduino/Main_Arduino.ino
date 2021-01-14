#include <Servo.h>
#include <PWM.h>
int y= 0;
int ir_pin1 = 2;
int ir_pin2 = 3;
int Servo_pin = 10;
int Stepper_pin = 9;
int Stepper_Direction = 8;
bool hitObject1 = false;
bool hitObject2 = false;
int counter1 = 0;
int counter2 = 0;
int condition = 0;
int a = 1;
int frequency = 500;
const int list_num = 6;
int list[list_num];
int list_index = 0;

void setup() {
  Serial.begin(9600);

  pinMode(ir_pin1, INPUT);
  pinMode(ir_pin2, INPUT);
  pinMode(Servo_pin,OUTPUT);

  InitTimersSafe();
  pinMode(Stepper_Direction, OUTPUT);
  pinMode(Stepper_pin, OUTPUT);
  SetPinFrequencySafe(Stepper_pin, frequency);
  SetPinFrequencySafe(Servo_pin, 50);
  digitalWrite(Stepper_Direction, LOW);

  for ( int i = 0; i < list_num; i++){
    list[i] = 0;
  }
}

void loop() {
  while (condition == 0) {
    if (Serial.available() > 0) {
      if (Serial.readString() == "Start") {
        condition = 1;
        pwmWrite(Stepper_pin, 127);
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

//Counter2______________________________________________________
int val2 = (digitalRead(ir_pin2));
  if ( (val2 == 0) && (hitObject2 == false) ) {
    counter2++;
    hitObject2 = true;
    Serial.print("ir_2 = ");
    Serial.println(counter2);
  }
  else if ( (val2 == 1) && (hitObject2 == true) ) {
    hitObject2 = false;
  }
  delay(5);


  
//BottleList_&_Stop_Program_________________________________________________
  if (Serial.available() > 0) {
      String pos = Serial.readString();
      if (pos == "Stop") {
      condition = 0;
      counter1 = 0;
      counter2 = 0;
      pwmWrite(Stepper_pin, 0);
    }
  else {
    condition = 1;
    list[list_index] = pos.toInt();
    list_index++;
    if (list_index >= list_num){
      list_index = 0;}
  }}
  
//Servo______________________________________________________________________  
  int FailBottle = 0;
  for ( int i = 0; i < list_num; i++){
   if (counter2 == list[i]){
    FailBottle++;}}
   if (FailBottle == 1){
     y = map(10,0,20,0,255);
     pwmWrite(Servo_pin, y);
   }
   else{y = map(1,0,20,0,255);
     pwmWrite(Servo_pin, y);
    
  
}}
}
