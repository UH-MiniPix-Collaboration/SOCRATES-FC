#include "uplink.h"
#include "downlink.h"

#define baudRate 4800

void setup() {
  Serial.begin(baudRate);

  actuator.attach(actuatorSignalPin);

  // Pins used for reading serial input
  pinMode(actuatorPin, OUTPUT);
  pinMode(motorPin, OUTPUT);

  // Multiplexer pins
  pinMode(pinOut_S0, OUTPUT);
  pinMode(pinOut_S1, OUTPUT);
  pinMode(pinOut_S2, OUTPUT);
}

void loop() {
  processCommands();
  buildPacket();
  delay(1000);
}