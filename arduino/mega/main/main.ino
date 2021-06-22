
// Pinouts
const int samplingPumpEnablePin = 2;
const int samplingPumpSpeedPin = 3;   //PWM
const int wastePumpDirectionPin = 8;
const int wastePumpSpeedPin = 9;      //PWM

// Durations (in milli-seconds)
const int t_samplingPumpStart = 500;
const int t_samplingPumpON = 52000;   //delaying this directly won't work as delay fn max out at 16383 (accurate delay)
const int t_wastePumpStart = 500;
const int t_wastePumpON = 10000;
const int t_waitBleach = 10000;

// Pump Speed (0 to 255)
const int samplingPumpSpeed = 255;
const int wastePumpSpeed = 255;

// String Input
String inputStringComputer = "";         // a string to store incoming data from Computer 
String inputStringOpentron = "";         // a string to store incoming data from Opentron 
boolean stringCompleteComputer = false;  // whether the string is complete (from Computer)
boolean stringCompleteOpentron = false;  // whether the string is complete (from Opentron)

// Commands //

String cmdError = "err?";

// Computer comm
String cmdStartSampling = "ssa?";
String cmdDoneSampling = "dsa?";

String cmdRemoveSampleAndClean = "rsc?";
String cmdDoneCleaning = "dcl?";

// Opentron comm
String cmdMoveNeedleForSampling = "mns?";
String cmdDoneMoveNeedleForSampling = "dmn?";

String cmdStartPreWash = "spr?";
String cmdDonePreWash = "dpr?";

String cmdStartBleach = "sbl?";
String cmdDoneBleach = "dbl?";

String cmdStartPostWash = "spo?";
String cmdDonePostWash = "dpo?";

boolean serialEventComputer() {
  while (Serial1.available()) {
    char inChar = (char)Serial1.read();
    inputStringComputer += inChar;
    if (inChar == '?') {
      stringCompleteComputer = true;
      return true;
    }
  }
  return false;
}

boolean serialEventOpentron() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputStringOpentron += inChar;
    if (inChar == '?') {
      stringCompleteOpentron = true;
      return true;
    }
  }
  return false;
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

void startWastePump(){
  digitalWrite(wastePumpDirectionPin, HIGH);
  analogWrite(wastePumpSpeedPin, wastePumpSpeed); // turn ON waste pump
  delay(t_wastePumpStart);
}

void stopWastePump(){
  analogWrite(wastePumpSpeedPin, 0);  
}

void removeWaste(){
  startWastePump();
  delay(t_wastePumpON);
  stopWastePump();
}

void setup() {
  Serial1.begin(9600);  // comm with computer
  Serial.begin(9600);   // comm with opentron
  inputStringComputer.reserve(50);  
  inputStringOpentron.reserve(50);  
  //while(!Serial1);
  //while(!Serial);
  pinMode(samplingPumpEnablePin, OUTPUT);
  digitalWrite(samplingPumpEnablePin, HIGH);
  pinMode(samplingPumpSpeedPin, OUTPUT);
}

// 52 seconds wait
void waitForEmptyTube(){
  delay(10000);
  delay(10000);
  delay(10000);
  delay(10000);
  delay(10000);
  delay(2000);  
}

void loop() {

    while(!serialEventComputer()){} // wait for sampling command from computer

    if (stringCompleteComputer){
      stringCompleteComputer = false;
      Serial1.print(inputStringComputer);
//      Serial.print(inputStringComputer);

      if (compareCmds(inputStringComputer,cmdStartSampling)){        
        inputStringComputer = "";
        startSamplingPump();
        Serial.print(cmdMoveNeedleForSampling); // send move needle command to opentron

        while(!serialEventOpentron()){} // wait for done move needle command from opentron

        if (stringCompleteOpentron){
          stringCompleteOpentron = false;

          Serial1.print(inputStringOpentron);

          if (compareCmds(inputStringOpentron,cmdDoneMoveNeedleForSampling)){
            inputStringOpentron = "";
            waitForEmptyTube();          // wait until the whole sample tube is emptied
            stopSamplingPump();          
            Serial1.print(cmdDoneSampling);   // send done sampling command to computer

            while(!serialEventComputer()){}   // wait for sample removal and clean command from computer

            if (stringCompleteComputer){
              stringCompleteComputer = false;

              if (compareCmds(inputStringComputer,cmdRemoveSampleAndClean)){
                inputStringComputer = ""; 

                removeWaste(); // remove sample from cyto tube
                
                startSamplingPump();
                Serial.print(cmdStartPreWash); // send pre-wash command to opentron

                while(!serialEventOpentron()){} // wait for done pre-wash command from opentron

                if (stringCompleteOpentron){
                  stringCompleteOpentron = false;
          
                  if (compareCmds(inputStringOpentron,cmdDonePreWash)){
                    inputStringOpentron = "";
                    waitForEmptyTube();          // wait until the whole sample tube is emptied
                    stopSamplingPump();
                    removeWaste();               // remove water from cyto tube

                    startSamplingPump();                              
                    Serial.print(cmdStartBleach); // send bleach command to opentron

                    while(!serialEventOpentron()){} // wait for done bleach command from opentron

                    if (stringCompleteOpentron){
                      stringCompleteOpentron = false;
              
                      if (compareCmds(inputStringOpentron,cmdDoneBleach)){
                        inputStringOpentron = "";
                        waitForEmptyTube();          // wait until the whole sample tube is emptied
                        stopSamplingPump();

                        delay(t_waitBleach);         // let bleach solution in cyto tube for 10 seconds 
                        removeWaste();               // remove bleach solution from cyto tube 

                        startSamplingPump();                                  
                        Serial.print(cmdStartPostWash); // send post-wash command to opentron

                        while(!serialEventOpentron()){} // wait for done post-wash command from opentron

                        if (stringCompleteOpentron){
                          stringCompleteOpentron = false;
                  
                          if (compareCmds(inputStringOpentron,cmdDonePostWash)){
                            inputStringOpentron = "";
                            waitForEmptyTube();          // wait until the whole sample tube is emptied
                            stopSamplingPump();
                            removeWaste();
                            
                            Serial1.print(cmdDoneCleaning);   // send done waste removal and clean command to computer          
                          }
                        }
                      }
                    }
                  }
              }
          }
        }
      }  
    }
  
}

}
}
