#include "uplink.h"
#include "downlink.h"

#define baudRate 4800


void setup() {
  Serial.begin(baudRate);

  // Set up servos
  stepper.begin(12, MICROSTEPS); // sets motor to RPM=12
  stepper.enable();
  actuator.attach(ACTUATOR_SIGNAL_PIN);

  // Multiplexer pins
  pinMode(pinOut_S0, OUTPUT);
  pinMode(pinOut_S1, OUTPUT);
  pinMode(pinOut_S2, OUTPUT);

  // PWM sweep pins
  pinMode(pwmPin1, OUTPUT);
  pinMode(pwmPin2, OUTPUT);
  pinMode(pwmPin3, OUTPUT);
  pinMode(pwmPin4, OUTPUT);
}

void loop() {
    processCommands();
    buildPacket();
    //autoCollectionArm(getAmbPressure());
    delay(1000);
}
