#include <ESP8266WiFi.h>
#include "FS.h"

String ID;
String PASS;

IPAddress noip(0,0,0,0);

String webpage = "<!DOCTYPE html> <html> <body> <form> SSID: <br> <input type=\"text\" name=\"SSID\"> <br> Password: <br> <input type=\"text\" name=\"Password\"> <br> <br> <input type=\"submit\" value=\"Submit\"> </form> </body> </html>";
unsigned long int counter;
unsigned long int blinkCounter;

int LED = D0;
int pirPin = D1;
int Relay = D2;
int Button = D3;

int motionTime; //global timer for motion
int motionEnable; //local motion enable, for timing etc
int relayDelay;
int timeout; //how long we want to set the motion timeout to

int isServer = 0; //if we are in server mode
int testMode;

WiFiServer server(12001);
WiFiServer server2(80);
WiFiClient client1;
 
void setup() 
{
  Serial.begin(9600);
  delay(10);
  SPIFFS.begin();
//  if (WiFi.localIP() == noip)
//  {
    //broadcastWiFi();
    //getFileInfo();
    connectWiFi();
//  }
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH); //turn off LED it is bright
  pinMode(pirPin, INPUT); //motion sensor input
  pinMode(Button, INPUT); //button input
  pinMode(Relay, OUTPUT);
  digitalWrite(Relay, LOW);
  counter = millis();
  motionEnable = 1;
  testMode = 0;
  blinkCounter = 0;
  timeout = 10000;
}

void getFileInfo()
{
  File f = SPIFFS.open("/wifi.txt","r");
  if (!f) {
    Serial.println("failed to open wifi file");
    return;
  }
  String wifiInfo = f.readString();
  Serial.println("Read in from file: \n" + wifiInfo);
  int line1 = wifiInfo.indexOf('\n');
  int line2 = wifiInfo.indexOf('\n',line1);
  int line3 = wifiInfo.indexOf('\n',line2);
  ID = wifiInfo.substring(0, line1);
  PASS = wifiInfo.substring(line1+1,line2);
  motionEnable = wifiInfo.substring(line2+1, line3).toInt();
  timeout = wifiInfo.substring(line3+1).toInt();
  Serial.println(ID+" "+PASS+" "+motionEnable+" "+timeout);
  //char* sid;
  //char* pas;
  //ID.toCharArray(sid,32);
  //PASS.toCharArray(pas,32);
  //ssid = sid;
  //password = pas;
}

void saveWiFiInfo(String html)
{
  int delimiter = html.indexOf("SSID=");
  int delimiter2 = html.indexOf('&');
  int delimiter3 = html.indexOf("Password=");
  int delimiter4 = html.indexOf(" HTTP");
  String ID = html.substring(delimiter+5, delimiter2);
  String PASS = html.substring(delimiter3+9, delimiter4);
  Serial.println("SSID = " + ID + " PASS = " + PASS + ".");
  File f = SPIFFS.open("/wifi.txt","w");
  if (!f) {
    Serial.println("failed to open wifi file");
    return;
  }
  f.println(ID+"\n"+PASS);
  f.close();
}

void connectWiFi()
{
  Serial.println("initial IP address: ");
  Serial.println(WiFi.localIP());
  if (WiFi.localIP() != noip)
  {
    Serial.println("Still connected to wifi!");
  //  return;
  }
 /* Serial.println();
  Serial.println("ID and PASS length are: " + String(ID.length()) + " " + String(PASS.length()));
  char ssid[ID.length()+1];
  char password[PASS.length()+1];
  ID.toCharArray(ssid,ID.length()+1);
  PASS.toCharArray(password,PASS.length()+1);*/
  char* ssid = "Pi_AP";
  char* password = "ThisPasswordIsStrong";
  Serial.print("Connecting to ");
  Serial.println(ssid);
  Serial.print("with password  ");
  Serial.println(password);
  WiFi.begin(ssid, password);
  unsigned long int time = millis();
  while (WiFi.status() != WL_CONNECTED && ((time + 10000) > millis()))
  {
    delay(100);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("Waiting for IP");
  time = millis();
  while (WiFi.localIP() == noip && ((time + 10000) > millis()))
  {
    delay(100);
    Serial.print(".");
  }
  Serial.println("");
  //Serial.println("WiFi connected");  
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  server.begin();
  if (WiFi.status() == WL_CONNECTED )//(WiFi.localIP() != noip)
  { //wtf BITCH
    isServer = 0;
    Serial.println("We are connected via Wireless!"); 
  }
  else
  {
    Serial.println("Still not connected to wifi");
  }
}

void broadcastWiFi()
{
  WiFi.mode(WIFI_AP);
  WiFi.softAP("TestMCU", "pass1234");
  server2.begin();
  isServer = 1; 
}

void serverLoop()
{
  client1 = server2.available();
  if (client1)
  {
    Serial.println("new client");
    client1.println(webpage);
    while(!client1.available())
    {
      delay(1);
    }
    String command = client1.readStringUntil('\r');
    Serial.println(command);
    if (command == "GET / HTTP/1.1")
    {
      return;
    }
    client1.flush();
    saveWiFiInfo(command);
    //String response = parseCmd(command);
    //Serial.println("Responding with: " + response);
    //client1.println(response);
    Serial.println("closing client");
    connectWiFi();
    return;
  }
}

String parseCmd(String command)
{
  String response = "";
  int delimiter = command.indexOf('&');
  int delimiter2 = command.indexOf('.');
  String cmd1 = command.substring(0, delimiter);
  String cmd2 = command.substring(delimiter+1, delimiter2);
  //Serial.println("Parsed commands to " + cmd1 + " and " + cmd2);
  if (cmd1 == "AUTH" && cmd2 == "HELLO")
  {
    response = "N0$fEr@tU";
    return response;
  }
  else if (cmd1 == "LED")
  {
    response = CtrlLED(cmd2);
    return response;
  }
  else if (cmd1 == "MOTION")
  {
    response = CtrlMotion(cmd2);
    return response;
  }
  else if (cmd1 == "RELAY")
  {
    if (cmd2 != "STATUS")
    {
      motionEnable = 0;
    }
    CtrlLED(cmd2);
    response = CtrlRelay(cmd2);
    return response;
  }
  else if (cmd1 == "STATUS")
  {
    response = CtrlLED("STATUS")+"&"+CtrlMotion("STATUS")+"&"+CtrlRelay("STATUS")+"&"+String(timeout);
    return response;
  }
  else if (cmd1 == "TIMEOUT")
  {
    timeout = cmd2.toInt();
    timeout = timeout *1000;
    Serial.println("timeout now set to: " + String(timeout) + "ms");
    return "OK";
  }
  else if (cmd1 == "TEST")
  {
    if (cmd2 == "START")
    {
      CtrlMotion("OFF");
      blinkCounter = 1000 + millis();
      testMode = 1;
      Serial.println("Now testing");
      return "OK";
    }
    else
    {
      CtrlMotion("ON");
      CtrlRelay("OFF");
      testMode = 0;
      Serial.println("Done testing");
      return "OK";
    }
  }
  response = "Error parsing";
  return response;  
}

void loop() 
{
  if (digitalRead(Button) == LOW)
  {//Toggle Relay state and disable motion
    CtrlRelay("TOGGLE");
    CtrlMotion("OFF");
  }
  if (isServer)
  {
    serverLoop();
    return;
  }
  if (testMode && (blinkCounter < millis()))
  {
    testEverything();
  }
  if (WiFi.status() == 6) //if wifi gets disconnected
  {
    ESP.reset();
  }
  motionSensor();
  client1 = server.available();
  if (client1)
  {
    Serial.println("");
    //Serial.println("new client");
    while(!client1.available())
    {
      delay(1);
    }
    String command = client1.readStringUntil('.');
    Serial.println(command);
    client1.flush();
    String response = parseCmd(command);
    Serial.println("Responding with: " + response);
    client1.println(response);
    client1.stop();
    //Serial.println("closing client");
    return;
  }
}

String CtrlMotion(String cmd2)
{
  String response = "ERROR";
  if(cmd2 == "STATUS")
  {
    response = motionEnable?"ON":"OFF";
  }
  else if(cmd2 == "ON")
  {
    motionEnable = 1;
    response = motionEnable?"ON":"OFF";
  }
  else if(cmd2 == "OFF")
  {
    motionEnable = 0;
    response = motionEnable?"ON":"OFF";
  }
  return response;
}

String CtrlLED(String cmd2)
{
  String response = "ERROR with LED command";
  if(cmd2 == "STATUS")
  {
    response = digitalRead(LED)?"OFF":"ON";
  }
  else if(cmd2 == "ON")
  {
    //motionEnable = 0;
    digitalWrite(LED, LOW);
    response = digitalRead(LED)?"OFF":"ON";
  }
  else if(cmd2 == "OFF")
  {
    digitalWrite(LED, HIGH);
    response = digitalRead(LED)?"OFF":"ON";
  }
  else if(cmd2 == "TOGGLE")
  {
    //motionEnable = 0;
    digitalWrite(LED, !digitalRead(LED));
    response = digitalRead(LED)?"OFF":"ON";
  }
  return response;
}

void motionSensor()
{
  if (motionEnable)
  {
    if (relayDelay <= millis())
    {
      motionTimer("CHECK");
      int pirVal = digitalRead(pirPin);
      if (pirVal == LOW)
      {
        //Serial.println("Motion Detected");
        CtrlLED("ON");
        CtrlRelay("ON");
        motionTimer("SET");
        return;
      }
    }
  }
}

void motionTimer(String cmd)
{
  if (cmd == "SET")
  {
    motionTime = millis()+timeout;
  }
  else if (cmd == "CHECK")
  {
    if (motionTime <= millis())
    {
      //Serial.println("Timer Expired");
      CtrlLED("OFF");
      CtrlRelay("OFF");
      relayDelay = millis() + 1750;
    }
  }
  return;
}

String CtrlRelay(String cmd)
{
  String response = "ERROR with Relay command";
  if(cmd == "STATUS")
  {
    response = digitalRead(Relay)?"ON":"OFF";
  }
  else if(cmd == "ON")
  {
    digitalWrite(Relay, HIGH);
    response = digitalRead(Relay)?"ON":"OFF";
  }
  else if(cmd == "OFF")
  {
    digitalWrite(Relay, LOW);
    response = digitalRead(Relay)?"ON":"OFF";
  }
  else if(cmd == "TOGGLE")
  {
    digitalWrite(Relay, !digitalRead(Relay));
    response = digitalRead(Relay)?"ON":"OFF";
  }
  return response;
}

void testEverything()
{
  blinkCounter = 500 + millis();
  CtrlLED("TOGGLE");
  CtrlRelay("TOGGLE");
}

