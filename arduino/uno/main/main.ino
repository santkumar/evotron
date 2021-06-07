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

void setup() {
  computerSerial.begin(9600);
  Serial.begin(9600);
  inputStringComputer.reserve(50);  
  inputStringOpentron.reserve(50);  
  //while(!computerSerial);
  //while(!Serial);
}

void loop() {

    int check1 = serialEventComputer();
    if (stringCompleteComputer){
      if (compareCmds(inputStringComputer,cmdStartSampling)){        
        computerSerial.print(cmdMoveNeedleForSampling);
        Serial.print(cmdMoveNeedleForSampling);
        while(!serialEventOpentron()){}
        if (stringCompleteOpentron){
          if (compareCmds(inputStringOpentron,cmdDone)){
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
