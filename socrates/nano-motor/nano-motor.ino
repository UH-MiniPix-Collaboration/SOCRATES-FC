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
bool previousRunBool;
bool runBool = false;

// 1600 steps is a full revolution
void spinStepperMotor() {
  //stepper.moveTo(stepper.currentPosition() + 1600);
  stepper.run();
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
void checkAccel(bool current, bool old){
     if (old != current) {
        if (current == false) {
          stepper.setAcceleration(-50);
        }else if (current == true){
          stepper.setAcceleration(50);
        }
     }
}

void setup() {
  stepper.setCurrentPosition(0);
  stepper.setMaxSpeed(4000);
  stepper.setAcceleration(50); // was 100, set back?

  pinMode(shutdownSignal, INPUT);
}

void loop() {
  if (digitalRead(shutdownSignal) == HIGH && !shutdown)
  {
    previousRunBool = runBool;
    runBool = false;
    checkAccel(runBool, previousRunBool);
    stepper.runToNewPosition(0);  // this call blocks, but should be fine. 
    //stepper.setMaxSpeed(0);  // likely not needed
    shutdown = true;
  }
  else if (!shutdown){
    previousRunBool = runBool;
    runBool = true;
    checkAccel(runBool, previousRunBool);
  }
  
  
  stepper.run();


}
