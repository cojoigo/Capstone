#include <SoftwareSerial.h>
#include <stdlib.h>
#include "EspCommunication.h"
#include "ArduinoController.h"
const char* SSID;
const char* PASS;
boolean discovered = false;
//SoftwareSerial wifiModule(6, 5); // TX, RX
unsigned long int counter;
EspCommunication *esp;
ArduinoController *arduino;

void setup()
{
  arduino = new ArduinoController(13); //gonna toggle pin 13 LED for starters
  esp = new EspCommunication(6, 5);
  Serial.begin(9600);
  esp->clearBuffer();
  Serial.println("Starting up now");
  esp->sendCmd("AT");
  esp->sendCmd("AT+CIPSTO?");
  counter = millis();
  //broadcastWiFi();
 // clearBuffer();
  esp->connectWiFi(SSID, PASS);
  //esp->broadcastWiFi();
  esp->sendCmd("AT+CIFSR"); //getIP
  delay(10);
}

void loop()
{
  unsigned long int time = millis();
 // if ((time - counter > 1000) || (time - counter < 0))
 // {
  //  arduino->toggleLED();
  //  counter = time;
 // }
  if(esp->available())
  {
    esp->listening();
  }
}
