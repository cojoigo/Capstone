/*
********************************************************************************
    EspCommunication.h - Library for communicating between the esp8266
    module and the Arduino
*********************************************************************************
*/
#ifndef EspCommunication_h
#define EspCommunication_h

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include "ArduinoController.h"

class EspCommunication
{
    public:
        EspCommunication();
        String sendCmd(String cmd, int wait = 200);
        String sendData(int connectionID, String data);
        void connectWiFi(const char* SSID, const char* PASS);
        void broadcastWiFi();
        void listening();
        void parseCmd(int connectionId, String command, String &cmd1, String &cmd2);
        void foundLEDCmd(int connectionId, String cmd2);
        void clearBuffer();
        int available();
    private:
        WiFiClient* wifiModule;
        ArduinoController* arduino;
};

#endif
