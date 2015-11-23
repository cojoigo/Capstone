#include "EspCommunication.h"
#include <SoftwareSerial.h>


EspCommunication::EspCommunication(int RX, int TX)
{
   if (wifiModule != NULL)
   {
      delete wifiModule;
   }
   wifiModule = new SoftwareSerial(RX, TX);
   wifiModule->begin(115200);
   sendCmd("AT+CIOBAUD=9600");
   wifiModule->end();
   wifiModule->begin(9600);
   arduino = new ArduinoController(13);
}

String EspCommunication::sendCmd(String cmd, int wait)
{
  String response = "";
  wifiModule->println("SEND: " + cmd);
  Serial.println("SEND: " + cmd); //for debug
  Serial.println("waiting for " + String(wait));
  unsigned long int time = millis();
  while ((time + wait) > millis())
  {
    while (wifiModule->available())
    {
      char c = wifiModule->read();
      response += c;
    }
  }
  Serial.print("Response is : ");
  Serial.println(response);//for debug
  if (response.substring(0) == "+IPD,") 
  {
    Serial.println("Found new command in response");
  }
  return response;
}

String EspCommunication::sendData(int connectionID, String data)
{
  String response = "";
  String cipSend = "AT+CIPSEND=";
  cipSend += connectionID;
  cipSend += ",";
  cipSend += data.length();
  sendCmd(cipSend, 100);
  wifiModule->println(data);
  Serial.println(data); //for debug
  unsigned long int time = millis();
  while ((time + 1000) > millis())
  {
    while (wifiModule->available())
    {
      char c = wifiModule->read();
      response += c;
    }
  }
  Serial.print("Response is : ");
  Serial.println(response);//for debug
  if (response.substring(0) == "+IPD,") 
  {
    Serial.println("Found new command in response");
  }
  return response;
}

void EspCommunication::connectWiFi(const char* SSID, const char* PASS)
{
  sendCmd("AT+CWMODE=1");
  String cmd = "AT+CWJAP=\"";
  cmd += "Pi_AP"; //SSID
  cmd += "\",\"";
  cmd += "Raspberry"; //PASS
  cmd += "\"";
  sendCmd(cmd, 5000);
  sendCmd("AT", 10);
  sendCmd("AT+CIFSR"); //getIP
  sendCmd("AT+CIPMUX=1");
  //sendCmd("AT+CIPSTART=\"UDP\",\"192.168.42.1\",12001");
  sendCmd("AT+CIPSERVER=1,12001");
}

void EspCommunication::broadcastWiFi()
{
  sendCmd("AT+CWMODE=2"); //configured as AP
  sendCmd("AT+CIFSR"); //getIP
  sendCmd("AT+CIPMUX=1");
  sendCmd("AT+CIPSERVER=1,8000"); //turning the server on port8000
  sendCmd("AT+CWSAP=\"TestNodeA1\",\"pass1234\",2,3",500); //set SSID,password,channel=1,encryption=3 (WPA2_PSK)
  clearBuffer();
}

void EspCommunication::listening()
{
  if (wifiModule->find("+IPD,"))
  {
    delay(10); //10ms delay to fill buffer
    int connectionId = 0;
    String msglength;
    char c = wifiModule->read();
    while(c != ',')
    {
      connectionId += c - '0';
      if (connectionId < 0) connectionId = 0;
      c = wifiModule->read();
    }
    Serial.println("");
    while(c != ':')
    {
      if (c == ',') c = wifiModule->read();
      msglength +=  c;
      c = wifiModule->read();
    }
    Serial.println("Connection ID = " + String(connectionId));
    Serial.println("Length = " + msglength);
    if (connectionId < 0) 
    {
      Serial.println("Error, connectionId < 0");
      connectionId = 0;
    }
    if (msglength.toInt() < 0) 
    {
      Serial.println("Error, msglength < 0");
      msglength = "16";
    }
    char cmd[msglength.toInt()];
    for (int i = 0; i < msglength.toInt() ; i++)
    {
      char c = wifiModule->read();
      Serial.print(c);
      if ((c == '\0') || (c == '\n'))
      {
        cmd[i] = c;
        break;
      }
      if (c != ':') cmd[i] = c;
    }
    Serial.println(" ");
    String command = String(cmd);  
    String cmd1, cmd2;
    parseCmd(connectionId, command, cmd1, cmd2);
   // Serial.println("Recieved commands to " + cmd1 + " and " + cmd2);
    sendCmd("AT+CIPCLOSE",100);
    clearBuffer();
  }
}

void EspCommunication::parseCmd(int connectionId, String command, String &cmd1, String &cmd2)
{
    int delimiter = command.indexOf('&');
    int delimiter2 = command.indexOf('.');
    cmd1 = command.substring(0,delimiter);
    cmd2 = command.substring(delimiter+1,delimiter2);
    Serial.println("Parsed commands to " + cmd1 + " and " + cmd2);
    if (cmd1 == "AUTH" && cmd2 == "HELLO")
    {
      String cipData = "N0$fEr@tU";
      sendData(connectionId, cipData);
      return;
    }
    else if (cmd1 == "LED")
    {
      foundLEDCmd(connectionId, cmd2);
      return;
    }
}

void EspCommunication::foundLEDCmd(int connectionId, String cmd2)
{  
  int LEDState;
  Serial.println("Found LED command");
  LEDState = arduino->LEDStatus();
  String cipData = "LED Status is";
  if(cmd2 == "STATUS")
  {
    if (LEDState==0) cipData += "OFF\r\n\n";
    else cipData += "ON\r\n\n";
    sendData(connectionId, cipData);
    return;
  }
  else if (cmd2 == "ON")
  {
    if (LEDState==0)
    {
      LEDState = arduino->toggleLED();
      if (LEDState == 1)
      {
        cipData += "changed to ON\r\n\n";
        sendData(connectionId, cipData);
        return;
      }
    }
  }
  else if (cmd2 == "OFF")
  {
    if (LEDState == 1)
    {
      LEDState = arduino->toggleLED();
      if (LEDState == 0)
      {
        cipData += "changed to OFF\r\n\n";
        sendData(connectionId, cipData);
        return;
      }
    }
  }
  //shouldn't ever fall through to here
  cipData += "ERROR\r\n\n";
  sendData(connectionId, cipData);
}
//void EspCommunication::foundRsp(String Response)

void EspCommunication::clearBuffer()
{
  Serial.println("Clearing buffer...");
  while (wifiModule->available() > 0)
  {
    char a = wifiModule->read();
    Serial.write(a);
  }
  Serial.println("*********Cleared************");
}

int EspCommunication::available()
{
  return wifiModule->available();
}
