#include <ESP8266WiFi.h>
#include "FS.h"

String ID;
String PASS;

IPAddress noip(0,0,0,0);

String webpage = "<!DOCTYPE html> <html> <body> <form> SSID: <br> <input type=\"text\" name=\"SSID\"> <br> Password: <br> <input type=\"text\" name=\"Password\"> <br> <br> <input type=\"submit\" value=\"Submit\"> </form> </body> </html>";
unsigned long int counter;

int LED = D0;
int pirPin = D1;
int Relay = D2;

int motionTime; //global timer for motion
int motionEnable; //local motion enable, for timing etc
int timeout; //how long we want to set the motion timeout to

int isServer = 0; //if we are in server mode
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
    //getWiFiInfo();
    connectWiFi();
//  }
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH); //turn off LED it is bright
  counter = millis();
  motionEnable = 1;
  timeout = 10000;
  pinMode(pirPin, INPUT); //motion sensor input
  pinMode(Relay, OUTPUT);
  digitalWrite(Relay, LOW);  
}

void getWiFiInfo()
{
  File f = SPIFFS.open("/wifi.txt","r");
  if (!f) {
    Serial.println("failed to open wifi file");
    return;
  }
  String wifiInfo = f.readString();
  Serial.println("Read in from file: \n" + wifiInfo);
  int delimiter = wifiInfo.indexOf('\n');
  ID = wifiInfo.substring(0, delimiter);
  PASS = wifiInfo.substring(delimiter+1);
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
  getWiFiInfo();
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
    response = CtrlLED("STATUS")+"&"+CtrlMotion("STATUS")+"&"+CtrlRelay("STATUS");
    return response;
  }
  else if (cmd1 == "TIMEOUT")
  {
    timeout = cmd2.toInt();
    timeout = timeout *1000;
    Serial.println("timeout now set to: " + String(timeout) + "s");
    return "OK";
  }
  response = "Error parsing";
  return response;  
}

void loop() 
{
  if (isServer)
  {
    serverLoop();
    return;
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
    unsigned long int time2 = millis();
    //client1.println(webpage);
    while(!client1.available())
    {
      delay(1);
    }
    Serial.println("Time to read is " + String((millis()-time2)));
    String command = client1.readStringUntil('.');
    Serial.println(command);
    client1.flush();
    String response = parseCmd(command);
    Serial.println("Responding with: " + response + " length is " + String(response.length()));
    client1.println(response);
    client1.stop();
    //Serial.println("closing client");
    Serial.println("Time open is " + String((millis()-time2)));
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
