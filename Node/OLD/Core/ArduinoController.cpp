#include "ArduinoController.h"

ArduinoController::ArduinoController(int LEDpin)
{
  pinMode(LEDpin, OUTPUT); //if LED is attached to pin 13
  _LEDpin = LEDpin;
}

boolean ArduinoController::toggleSwitch()
{
  int input = 2;
  int output = 13;
  int state = HIGH, reading, previous = LOW; //defaults
  pinMode(input, INPUT);
  pinMode(output, OUTPUT);
  reading = digitalRead(input);
  //below will toggle a switch
  if (reading == HIGH && previous == LOW)
  {
    if (state == HIGH) state = LOW;
    else state = HIGH;
  }
  digitalWrite(output, state);
  previous = reading;
  return (reading ? HIGH : LOW);
}

boolean ArduinoController::toggleLED()
{
  digitalWrite(_LEDpin, !digitalRead(_LEDpin));
  return digitalRead(_LEDpin);
}

boolean ArduinoController::LEDStatus()
{
  return digitalRead(_LEDpin);
}
