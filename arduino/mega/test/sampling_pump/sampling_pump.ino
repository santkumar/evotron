// Pinouts
const int samplingPumpEnablePin = 2;
const int samplingPumpSpeedPin = 3;   //PWM

const int wastePumpDirectionPin = 8;
const int wastePumpSpeedPin = 9;      //PWM

// Durations (in milli-seconds)
const int t_samplingPumpStart = 500;
const int t_samplingPumpON = 5000;
const int t_wastePumpStart = 500;
const int t_wastePumpON = 5000;

// Pump Speed (0 to 255)
const int samplingPumpSpeed = 255;
const int wastePumpSpeed = 255;

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

void setup() {
  pinMode(samplingPumpEnablePin, OUTPUT);
  pinMode(samplingPumpSpeedPin, OUTPUT);
  pinMode(wastePumpSpeedPin, OUTPUT);
  pinMode(wastePumpDirectionPin, OUTPUT);

  digitalWrite(samplingPumpEnablePin, HIGH); // turn OFF sampling pump
  analogWrite(wastePumpSpeedPin,0); // turn OFF waste pump
}

void loop() {

startSamplingPump();
delay(t_samplingPumpON);
stopSamplingPump();

startWastePump();
delay(t_wastePumpON);
stopWastePump();
  
} 
