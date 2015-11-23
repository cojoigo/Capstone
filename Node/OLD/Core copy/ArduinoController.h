/*
********************************************************************************
    ArduinoController.h - Library for controlling the Arduino
*********************************************************************************
*/
#ifndef ArduinoController_h
#define ArduinoController_h

#include <Arduino.h>

class ArduinoController
{
    public:
        ArduinoController(int LEDpin);
        boolean toggleSwitch();
        boolean toggleLED();
        boolean LEDStatus();
    private:
        int _LEDpin;
        int _RelayPin;
        int _MotionSensorPin;
};

#endif
