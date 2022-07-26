// Recurring Command: 'od_ledr,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,_!"
// Immediate Command: 'od_ledi,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,_!"
// Acknowledgement to Run: "od_leda,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,_!"

// Recurring Command: 'opto_ledr,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,_!"
// Immediate Command: 'opto_ledi,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,_!"
// Acknowledgement to Run: "opto_leda,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,_!"

#include <evolver_si.h>
#include <Tlc5940.h>

// String Input
String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete
boolean serialAvailable = true;  // if serial port is ok to write on

//General Serial Communication
String comma = ",";
String end_mark = "end";
int num_vials = 16;
int active_vial = 0;

// OD LED Settings
String od_led_address = "od_led";
evolver_si od_led("od_led", "_!", num_vials+1); // 17 CSV-inputs from RPI
boolean new_odLEDinput = false;
int saved_odLEDinputs[] = {4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095};

// OPTO LED Settings
String opto_led_address = "opto_led1";
evolver_si opto_led("opto_led1", "_!", num_vials+1); // 17 CSV-inputs from RPI
boolean new_optoLEDinput = false;
int saved_optoLEDinputs[] = {4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095};

void setup() {
  pinMode(12, OUTPUT);
  digitalWrite(12, LOW);
  Tlc.init(RIGHT_PWM | LEFT_PWM,4095); // for both OD and OPTO LED (Left is OD and Right is OPTO)
  Serial1.begin(9600);
  SerialUSB.begin(9600);
  // reserve 1000 bytes for the inputString:
  inputString.reserve(1000);
  while (!Serial1);

  for (int i = 0; i < num_vials; i++) {
    Tlc.set(LEFT_PWM, i, 4095 - saved_odLEDinputs[i]);
  }
  while(Tlc.update());

  for (int i = 0; i < num_vials; i++) {
    Tlc.set(RIGHT_PWM, i, 4095 - saved_optoLEDinputs[i]);
  }
  while(Tlc.update());

}

void loop() {
  serialEvent();
  if (stringComplete) {
    SerialUSB.println(inputString);
    od_led.analyzeAndCheck(inputString);
    opto_led.analyzeAndCheck(inputString);

    // Clear input string, avoid accumulation of previous messages
    inputString = "";
        
    // OD LED Logic
    if (od_led.addressFound) {
      if (od_led.input_array[0] == "i" || od_led.input_array[0] == "r") {
        SerialUSB.println("Saving OD LED Setpoints");
        for (int n = 1; n < num_vials+1; n++) {
          saved_odLEDinputs[n-1] = od_led.input_array[n].toInt();
        }
        
        SerialUSB.println("Echoing New OD LED Command");
        new_odLEDinput = true;
        echoODLED();
        
        SerialUSB.println("Waiting for OK to execute...");
      }
      if (od_led.input_array[0] == "a" && new_odLEDinput) {
        update_odLEDvalues();
        SerialUSB.println("Command Executed!");
        new_odLEDinput = false;               
      }
      
      od_led.addressFound = false;
      inputString = "";
    }

    // OPTO LED Logic
    if (opto_led.addressFound) {
      if (opto_led.input_array[0] == "i" || opto_led.input_array[0] == "r") {
        SerialUSB.println("Saving OPTO LED Setpoints");
        for (int n = 1; n < num_vials+1; n++) {
          saved_optoLEDinputs[n-1] = opto_led.input_array[n].toInt();
        }
        
        SerialUSB.println("Echoing New OPTO LED Command");
        new_optoLEDinput = true;
        echoOPTOLED();
        
        SerialUSB.println("Waiting for OK to execute...");
      }
      if (opto_led.input_array[0] == "a" && new_optoLEDinput) {
        update_optoLEDvalues();
        SerialUSB.println("Command Executed!");
        new_optoLEDinput = false;               
      }
      
      opto_led.addressFound = false;
      inputString = "";
    }

    // Clears strings if too long
    // Should be checked server-side to avoid malfunctioning
    if (inputString.length() > 2000){
      SerialUSB.println("Cleared Input String");
      inputString = "";
    }
  }

  // clear the string:
  stringComplete = false;
}

void serialEvent() {
  while (Serial1.available()) {
    char inChar = (char)Serial1.read();
    inputString += inChar;
    if (inChar == '!') {
      stringComplete = true;
      break;
    }
  }
}

void echoODLED() {
  digitalWrite(12, HIGH);
  
  String outputString = od_led_address + "e,";
  for (int n = 1; n < num_vials+1 ; n++) {
    outputString += od_led.input_array[n];
    outputString += comma;
  }
  outputString += end_mark;
  delay(100);
  if (serialAvailable) {
    SerialUSB.println(outputString);
    Serial1.print(outputString);
  }  
  delay(100);
  digitalWrite(12, LOW);
}

void echoOPTOLED() {
  digitalWrite(12, HIGH);
  
  String outputString = opto_led_address + "e,";
  for (int n = 1; n < num_vials+1 ; n++) {
    outputString += opto_led.input_array[n];
    outputString += comma;
  }
  outputString += end_mark;
  delay(100);
  if (serialAvailable) {
    SerialUSB.println(outputString);
    Serial1.print(outputString);
  }  
  delay(100);
  digitalWrite(12, LOW);
}

void update_odLEDvalues() {
  for (int i = 0; i < num_vials; i++) {
    Tlc.set(LEFT_PWM, i, 4095 - saved_odLEDinputs[i]);
  }
  while(Tlc.update());
}

void update_optoLEDvalues() {
  for (int i = 0; i < num_vials; i++) {
    Tlc.set(RIGHT_PWM, i, 4095 - saved_optoLEDinputs[i]);
  }
  while(Tlc.update());
}
