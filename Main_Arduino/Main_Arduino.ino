#include <Servo.h>
#include <PWM.h>
Servo myservo;

int ir_pin1 = 2;
int ir_pin2 = 3;
bool hitObject1 = false;
bool hitObject2 = false;
int counter1 = 0;
int counter2 = 0;
int condition = 0;
int a = 1;
int frequency = 1700;
const int list_num = 6;
int list[list_num];
int list_index = 0;

void setup() {
  Serial.begin(9600);

  pinMode(ir_pin1, INPUT);
  pinMode(ir_pin2, INPUT);
  myservo.attach(6);

  InitTimersSafe();
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  SetPinFrequencySafe(9, frequency);
  digitalWrite(8, LOW);

  for ( int i = 0; i < list_num; i++){
    list[i] = 0;
  }
}

void loop() {
  while (condition == 0) {
    if (Serial.available() > 0) {
      
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
      String pos = Serial.readStringUntil('\n');
      if (pos == "Stop") {
      condition = 0;
      counter1 = 0;
      counter2 = 0;
      pwmWrite(9, 0);
    }
  else {
   
    condition = 1;
    list[list_index] = pos.toInt();
    list_index++;
    if (list_index >= list_num){
      list_index = 0;}
    Serial.println('[');
     for ( int i = 0; i < list_num; i++){
      Serial.print(list[i]);
      Serial.print(',');
     }
     Serial.print(']');
  }}
  
//Servo______________________________________________________________________  
  int FailBottle = 0;
  for ( int i = 0; i < list_num; i++){
   if (counter2 == list[i]){
    FailBottle++;}}
   if (FailBottle == 1){
    myservo.write(90);
   }
   else{myservo.write(0);
}}
delay(400);
}
