uint16_t t;
uint16_t icr = 0xffff;

//---------------Configurations------------------------------
void configtoPWM16() {
  DDRB |= _BV(PB1) | _BV(PB2); //Set pins as outputs
  TCCR1A = _BV(COM1A1) | _BV(COM1B1) //Non-Inv PWM
           | _BV(WGM11); // Mode 14: Fast PWM, TOP=ICR1
  TCCR1B = _BV(WGM13) | _BV(WGM12)
           | _BV(CS10); // Prescaler 1
  ICR1 = icr; // TOP counter value (Relieving OCR1A*)
}
void Write16(uint8_t pin, uint16_t val) {
  switch (pin) {
    case  9: OCR1A = val; break;
    case 10: OCR1B = val; break;
  }
}
