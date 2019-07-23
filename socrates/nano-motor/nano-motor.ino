// This script will allow the Arduino Nano to control the stepper motor.

// Documentation for AccelStepper:
// http://www.airspayce.com/mikem/arduino/AccelStepper/classAccelStepper.html

#include <Arduino.h>
#include <Servo.h>
#include "include/StepperDriver/AccelStepper.h"
#include "include/StepperDriver/AccelStepper.cpp"
#include "include/StepperDriver/BasicStepperDriver.h"
#include "include/StepperDriver/BasicStepperDriver.cpp"


#define shutdownSignal 11  // Listen for signal to shutdown motor

// (DIR, STEP, M0, M1)
AccelStepper stepper(AccelStepper::FULL4WIRE, 3, 4, 9, 8);
bool shutdown = false;

// 1600 steps is a full revolution
void spinStepperMotor() {
  stepper.moveTo(stepper.currentPosition() + 1600);
}

void stopStepperMotor() {
  long currentPos = stepper.currentPosition();
  long stepsInRev = currentPos % 1600;
  long stepsToZero = 1600 - stepsInRev + 1600;
  long finalPos = currentPos + stepsToZero;
  stepper.moveTo(finalPos);

  // Debug prints
  /*
    Serial.print("stepsInRev: ");
    Serial.println(stepsInRev);
    Serial.print("stepsToZero: ");
    Serial.println(stepsToZero);
    Serial.print("finalPos: ");
    Serial.println(finalPos);
  */
}

void setup() {
  stepper.setCurrentPosition(0);
  stepper.setMaxSpeed(4000);
  stepper.setAcceleration(100);

  pinMode(shutdownSignal, INPUT);
}

void loop() {
  if (digitalRead(shutdownSignal) == HIGH && !shutdown)
  {
    stopStepperMotor();
    shutdown = true;
  }
  else if (!shutdown)
    spinStepperMotor();
  stepper.run();
  //delay(100);  // Do we need a delay here?
}
