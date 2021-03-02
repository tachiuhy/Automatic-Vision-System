#include <Wire.h>
#define SLAVE_ADDR 9
#define ANSWERSIZE 2

int ir_pin2 = 3;
bool hitObject2 = false;
int counter2 = 0;

int y;
int k;
int angle = 120;

int list_index = 0;
const int list_num = 6;
int list[list_num];

int x;


void setup() {
  Wire.begin(SLAVE_ADDR);

  Serial.begin(9600);
  Serial.setTimeout(5);

  pinMode(10, OUTPUT);
  pinMode(ir_pin2, INPUT);

  //  Start posítion
  configtoPWM16();
  Write16(10, 11500);

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
    Serial.print("x: ");
    Serial.println(x);
    if (x == 0) {
      counter2 = 0;
    }
    else {
      list[list_index] =  x;
      list_index++;
      if (list_index >= list_num) {
        list_index = 0;
      }
      Serial.print('[');
      for ( int i = 0; i < list_num; i++) {
        Serial.print(list[i]);
        Serial.print(',');
      }
      Serial.println(']');

    }
  }
  //Servo__________

  for (int i = 0; i < list_num; i++) {
    if (counter2 == list[i] && counter2 != 0) {
      list[i] = 0;
      Serial.println('c');

      for (int t = 0; t < 800; t++) {
        y = map(angle, 0, 180, 11500, 41550 );
        Write16(10, y);
        delay(1);
      }

      for (int t = 0; t < 800; t++) {
        k = (angle - pow(1.5, t));

        if ((k > 0) && (k < angle)) {
//          Serial.println(k);
          y = map(k, 0, 180, 11500, 41550);
          Write16(10, y);
          delay(90);
        }

        else if (k < 0) {
          y = map(0, 0, 180, 11500, 41550);
          Write16(10, y);
        }
      }

    }
  }
}

void receiveEvent() {
  while ( Wire.available() > 1) {
    x = Wire.read();

  }
}
