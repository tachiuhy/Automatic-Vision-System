#include <PWM.h>
#include <Wire.h>
#define SLAVE_ADDR 9
#define ANSWERSIZE 2

int ir_pin2 = 3;
bool hitObject2 = false;
int counter2 = 0;

int y;
int pos;
int angle;
unsigned long previousMillis = 0;
const long interval = 500;  // mS
unsigned long currentMillis;

int list_index = 0;
const int list_num = 6;
int list[list_num];

int x;

void setup() {
  Wire.begin(SLAVE_ADDR);
  Serial.begin(9600);

  InitTimersSafe();
  SetPinFrequency(10, 50);
  pinMode(10, OUTPUT);
  Serial.setTimeout(5);
  pinMode(ir_pin2, INPUT);
  //  Start posítion
  y = map(2, 0, 50, 0, 255 );
  pwmWrite(10, y);

  for ( int i = 0; i < list_num; i++) {
    list[i] = 0;
  }
  Wire.onReceive(receiveEvent);
}

void loop() {

  //Counter2______________________________________________________
  int val2 = (digitalRead(ir_pin2));
  if ( (val2 == 0) && (hitObject2 == false) ) {
    counter2++;
    hitObject2 = true;
    Serial.println(counter2);
  }
  else if ( (val2 == 1) && (hitObject2 == true) ) {
    hitObject2 = false;
  }
  delay(5);
  if (Wire.available() > 0 ) {
    x = Wire.read();
    if (x == 0) {
      counter2 = 0;
    }
    else {
      list[list_index] = x;
      list_index++;
      if (list_index >= list_num) {
        list_index = 0;
      }
//      Serial.println('[');
//      for ( int i = 0; i < list_num; i++) {
//        Serial.print(list[i]);
//        Serial.print(',');
//      }
//      Serial.print(']');

    }
  }
//Servo__________
  
  for (int i = 0; i < list_num; i++) {
    if (counter2 == list[i] && counter2 != 0) {
      list[i] = 0; 
      Serial.print('c');    
      int  angle  = 47;
      pos = (angle / 18.0) + 2;
      
      for (int t = 0; t < 500; t++){
      y = map(pos, 0, 50, 0, 255 );
      pwmWrite(10, y);
      delay(1);}
      for (int t = 0; t < 500; t++){
      y = map(2, 0, 50, 0, 255 );
      pwmWrite(10, y);
      delay(1);}
      
   }}
}

void receiveEvent() {
  while ( Wire.available() > 1) {
    x = Wire.read();
  }
}
