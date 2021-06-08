#include <SoftwareSerial.h>

// Pinouts
const int samplingPumpEnablePin = 2;
const int samplingPumpSpeedPin = 5;

// Durations (in milli-seconds)
const int t_samplingPumpStart = 500;
const int t_samplingPumpON = 5000;

// Pump Speed (0 to 255)
const int samplingPumpSpeed = 255;

// String Input
String inputStringComputer = "";         // a string to store incoming data from Computer 
String inputStringOpentron = "";         // a string to store incoming data from Opentron 
boolean stringCompleteComputer = false;  // whether the string is complete (from Computer)
boolean stringCompleteOpentron = false;  // whether the string is complete (from Opentron)

// Commands
String cmdStartSampling = "ss?";
String cmdCytoAcquisitionStarted = "as?";
String cmdCytoAcquisitionFinished = "af?";
String cmdRemoveWaste = "rw?";
String cmdCleanNeedle = "cn?";
String cmdDone = "dn?";
String cmdMoveNeedleForSampling = "mn?";
String cmdError = "er?";

SoftwareSerial computerSerial(10, 11); // RX, TX (connection with Computer)

int serialEventComputer() {
  while (computerSerial.available()) {
    char inChar = (char)computerSerial.read();
    inputStringComputer += inChar;
    if (inChar == '?') {
      stringCompleteComputer = true;
      return 1;
    }
  }
  return 0;
}

int serialEventOpentron() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputStringOpentron += inChar;
    if (inChar == '?') {
      stringCompleteOpentron = true;
      return 1;
    }
  }
  return 0;
}

boolean compareCmds(String str1, String str2){
  int i;
  int len1 = sizeof(str1);
  int len2 = sizeof(str2);
  if (len1!=len2) return false;
  for (i=0; i<len1; i++) if (str1[i]!=str2[i]) return false;
  return true;
}

void startSamplingPump(){
  analogWrite(samplingPumpSpeedPin,samplingPumpSpeed);
  digitalWrite(samplingPumpEnablePin, LOW); // turn ON sampling pump
  delay(t_samplingPumpStart);  
}

void stopSamplingPump(){
  digitalWrite(samplingPumpEnablePin, HIGH);
  analogWrite(samplingPumpSpeedPin,0);
}

void setup() {
  computerSerial.begin(9600);
  Serial.begin(9600);
  inputStringComputer.reserve(50);  
  inputStringOpentron.reserve(50);  
  //while(!computerSerial);
  //while(!Serial);
  pinMode(samplingPumpEnablePin, OUTPUT);
  digitalWrite(samplingPumpEnablePin, HIGH);
  pinMode(samplingPumpSpeedPin, OUTPUT);
}

void loop() {

    int check1 = serialEventComputer();
    if (stringCompleteComputer){
      computerSerial.print(inputStringComputer);
      if (compareCmds(inputStringComputer,cmdStartSampling)){        
        computerSerial.print(cmdMoveNeedleForSampling);
        startSamplingPump();
        Serial.print(cmdMoveNeedleForSampling);
        while(!serialEventOpentron()){}
        if (stringCompleteOpentron){
          if (compareCmds(inputStringOpentron,cmdDone)){
            delay(t_samplingPumpON);
            analogWrite(samplingPumpSpeedPin,100);
            delay(t_samplingPumpON);
            stopSamplingPump();          
            computerSerial.print(cmdDone);
            stringCompleteOpentron = false;
            inputStringOpentron = "";            
          }
        }
        stringCompleteComputer = false;
        inputStringComputer = "";
        delay(100);
      }  
    }
  
} 
