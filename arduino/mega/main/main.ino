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
String cmdMoveNeedleForSampling = "mnfs?";

// SoftwareSerial computerSerial(10, 11); // RX, TX (connection with Computer)

void setup() {
  Serial1.begin(9600);
  Serial.begin(9600);
  inputStringComputer.reserve(100);  
  inputStringOpentron.reserve(100);  
  //while(!computerSerial);
  //while(!Serial);
}


void loop() {

    if (stringCompleteComputer){
      //if (inputStringComputer==cmdStartSampling){        
        // Serial.print(cmdMoveNeedleForSampling);
        //while(!serialEventOpentron()){}
        Serial1.print(cmdDone);
        stringCompleteComputer = false;
        inputStringComputer = "";
        delay(100);
      //}  
    } 
}

void serialEvent1() {
  while (Serial1.available()) {
    char inChar = (char)Serial1.read();
    inputStringComputer += inChar;
    if (inChar == '?') {
      stringCompleteComputer = true;
      break;
    }
  }
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputStringOpentron += inChar;
    if (inChar == '?') {
      stringCompleteOpentron = true;
      break;
    }
  }
}
