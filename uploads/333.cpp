#include <Servo.h>

/**
 * Copyright (c) Clemens Elflein @ 2016
 * 
 * This code is used for the actuator board
 */

 // PINS
 #define PIN_RELAIS 4
 #define PIN_STEERING 6
 #define PIN_STEERING_REAR 9
 #define PIN_POTI_STEER_FRONT A5
 #define PIN_POTI_STEER_REAR A4
 
 #define PIN_SPEED 5
 #define PIN_RC_MUX A2
 
// Magic, don't ask..
 #define SPEED_OFFSET_US 190

 #define PIN_LIGHT_TL 11
 #define PIN_LIGHT_TR 10
 #define PIN_LIGHT_REV 3
 #define PIN_LIGHT_HL 12
 #define PIN_LIGHT_BRK 8
 #define PIN_LED_ONBOARD 13

 #define WATCHDOG_MS 300

 #define ARDUINO_ID "AC"

// In degrees
 #define STEER_POTI_INFLUENCE 15.0

// Light state. Default: Off
// | REV | HEADLIGHT | BREAK | TURNL | TURNR |
 byte lightMask = 0;
 byte controlMask = 0;
 byte speedWanted = 90;
 byte steeringWanted = 90;
 byte steeringRearWanted = 90;

 byte speedRC = 90;
 byte steeringRC = 90;
 
// Used for turn signal
unsigned long startMillis = 0;
unsigned long watchdogTimestamp;
byte turnSignalState = 0;

Servo servSpeed;
Servo servSteering;
Servo servSteeringRear;
void setup() {
  pinMode(PIN_RELAIS, OUTPUT);
  pinMode(PIN_STEERING, OUTPUT);
  pinMode(PIN_STEERING_REAR, OUTPUT);
  pinMode(PIN_SPEED, OUTPUT);
  pinMode(PIN_LIGHT_TL, OUTPUT);
  pinMode(PIN_LIGHT_TR, OUTPUT);
  pinMode(PIN_LIGHT_REV, OUTPUT);
  pinMode(PIN_LIGHT_HL, OUTPUT);
  pinMode(PIN_LIGHT_BRK, OUTPUT);
  pinMode(PIN_LED_ONBOARD, OUTPUT);
  pinMode(PIN_POTI_STEER_FRONT, INPUT);
  pinMode(PIN_POTI_STEER_REAR, INPUT);
  pinMode(PIN_RC_MUX, OUTPUT);
  

  // We want this always on
  digitalWrite(PIN_RELAIS, HIGH);

  // Attach the servos and stop
  servSpeed.attach(PIN_SPEED,1000-SPEED_OFFSET_US, 2000);
  servSteering.attach(PIN_STEERING);
  servSteeringRear.attach(PIN_STEERING_REAR);
  servSpeed.writeMicroseconds(1500-SPEED_OFFSET_US);
  servSteering.write(90);
  servSteeringRear.write(90);

  digitalWrite(PIN_RC_MUX, HIGH);
  

  resetWatchdog();

  Serial.begin(1000000);
}

void loop() {

  double steerOffsetF = (double)analogRead(PIN_POTI_STEER_FRONT)/1024.0;
  steerOffsetF -= .5;
  steerOffsetF *= 2.0 * STEER_POTI_INFLUENCE;
  double steerOffsetR = (double)analogRead(PIN_POTI_STEER_REAR)/1024.0;
  steerOffsetR -= .5;
  steerOffsetR *= 2.0 * STEER_POTI_INFLUENCE;



  readPacket();

  // Check watchdog. If it is too old, switch to RC
  if(millis() - watchdogTimestamp > WATCHDOG_MS) {
    controlMask = 0;
  }

  bool isRC = false;
  digitalWrite(PIN_RC_MUX, isRC);
  digitalWrite(PIN_LED_ONBOARD, isRC);
  

  
  
  // Set Lights
  digitalWrite(PIN_LIGHT_REV, lightMask & 0b10000);
  digitalWrite(PIN_LIGHT_HL, lightMask & 0b01000);
  digitalWrite(PIN_LIGHT_BRK, lightMask & 0b00100);
  
  if(millis() - startMillis > (controlMask ? 500 : 100)) {
    startMillis = millis();
    turnSignalState = ~turnSignalState;

    // Write an empty packet, so that the receiving side knows that we are the actuator
    Serial.print("AC0000\r\n");
    
    if(controlMask) {
      // Controlled by CAR
      digitalWrite(PIN_LIGHT_TL, turnSignalState & lightMask & 0b00010);
      digitalWrite(PIN_LIGHT_TR, turnSignalState & lightMask & 0b00001);
    } else {
      // Controlled by RC
      digitalWrite(PIN_LIGHT_TL, turnSignalState);
      digitalWrite(PIN_LIGHT_TR, turnSignalState);
    }
  }


  if(controlMask & 0b10) {
    // Magic, don't ask.
    int speedUS = ((((float)speedWanted)/180.0f)-0.5f)*1000.0 + 1500.0 - SPEED_OFFSET_US;
    servSpeed.writeMicroseconds(speedUS);  
  } else {
    // Magic, don't ask.
    int speedUS = ((((float)speedRC)/180.0f)-0.5f)*1000.0 + 1500.0 - SPEED_OFFSET_US;
    servSpeed.writeMicroseconds(speedUS);  
  }

  if(controlMask & 0b01) {
    servSteering.write(steeringWanted + steerOffsetF);
    servSteeringRear.write(steeringRearWanted + steerOffsetR);
  } else {
    servSteering.write(steeringRC + steerOffsetF);
    servSteeringRear.write(steeringRC + steerOffsetR);
  }
}

void readPacket() {
  // Wait for 13
  while(Serial.available() > 0 && Serial.peek() != '\n') {
    Serial.read();
  }

  
  // We have newline on top, wait for enough data
  if(Serial.available() < 11)
    return;
  // Read newline
  Serial.read();
  // Read light, control, speed, steering
  lightMask = readHex();
  controlMask = readHex();
  speedWanted = readHex();
  steeringWanted = readHex();
  steeringRearWanted = readHex();

  steeringWanted = constrain(steeringWanted, 50, 130);
  steeringRearWanted = constrain(steeringRearWanted, 50, 130);

  resetWatchdog();
}

void resetWatchdog() {
  watchdogTimestamp = millis();
}

byte readHex() {
  byte first = unhex(Serial.read());
  byte second = unhex(Serial.read());
  return first << 4 | second;
}

byte unhex(byte b) {
  if(b >= '0' && b <= '9')
    return b-'0';
  if(b >= 'A' && b <= 'F')
    return b-'A'+10;
  return b-'a'+10;
}
 
