#include <SoftwareSerial.h>

// String Input
String inputStringComputer = "";         // a string to store incoming data from Computer 
String inputStringOpentron = "";         // a string to store incoming data from Opentron 
boolean stringCompleteComputer = false;  // whether the string is complete (from Computer)
boolean stringCompleteOpentron = false;  // whether the string is complete (from Opentron)

// Commands
String cmdStartSampling = "ss?";
String cmdCytoAcquisitionStarted = "cas?";
String cmdCytoAcquisitionFinished = "caf?";
String cmdRemoveWaste = "rw?";
String cmdCleanNeedle = "cn?";
String cmdDone = "d?";

SoftwareSerial computerSerial(10, 11); // RX, TX (connection with Computer)

void serialEventComputer() {
  while (computerSerial.available()) {
    char inChar = (char)computerSerial.read();
    inputStringComputer += inChar;
    if (inChar == '?') {
      stringCompleteComputer = true;
      break;
    }
  }
}

void serialEventOpentron() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputStringOpentron += inChar;
    if (inChar == '?') {
      stringCompleteOpentron = true;
      break;
    }
  }
}

void setup() {
  computerSerial.begin(9600);
  Serial.begin(9600);
  inputStringComputer.reserve(100);  
  inputStringOpentron.reserve(100);  
  while(!computerSerial);
  while(!Serial);
}


void loop() {

    serialEventComputer();
    if (stringCompleteComputer){
      if (inputStringComputer==cmdStartSampling){        
        computerSerial.print(cmdDone);
        stringCompleteComputer = false;
        inputStringComputer = "";
        delay(100);
      }  
    }
  
}
