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
  stepper.moveTo(stepper.currentPosition() + 1600);
  //stepper.run();
}

long stepsToZero() {                             // was formally Reed's stopStepperMotor function. 
  long currentPos = stepper.currentPosition();   // to return it, uncomment 33 and 34 and remove 32, and make it a void function
  long stepsInRev = currentPos % 1600;
  long stepsToZero = 1600 - stepsInRev + 1600;
  return stepsToZero;
  //long finalPos = currentPos + stepsToZero;
  //stepper.moveTo(finalPos);                     // moveTo call may not work because target pos never set (doesnt work in call)
  

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
void checkAccel(boolean current, boolean old){
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
  stepper.setMaxSpeed(4000);  // may be too fast for processor to handle. 
  stepper.setAcceleration(50); // was 100, set back?

  pinMode(shutdownSignal, INPUT);
}

void loop() {
  if (digitalRead(shutdownSignal) == HIGH && !shutdown)
  {
    previousRunBool = runBool;
    runBool = false;
    checkAccel(runBool, previousRunBool);
    stepper.runToNewPosition(stepsToZero() + 1600);  // this call blocks, but should be fine. Allows 1 full rev to slow down. 
    shutdown = true;
    stepper.run();
  }
  else if (!shutdown){
    previousRunBool = runBool;
    runBool = true;
    checkAccel(runBool, previousRunBool);
    spinStepperMotor();                    // this line is only one new from when we worked in hotel. If error try removing this 1st
    stepper.run();
  }
  
  
  stepper.run();


}
