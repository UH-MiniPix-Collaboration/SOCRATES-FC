#include <Arduino.h>
#include <Servo.h>
#include "include/StepperDriver/AccelStepper.h"
#include "include/StepperDriver/AccelStepper.cpp"
#include "include/StepperDriver/BasicStepperDriver.h"
#include "include/StepperDriver/BasicStepperDriver.cpp"

// Documentation for AccelStepper:
// http://www.airspayce.com/mikem/arduino/AccelStepper/classAccelStepper.html

// Code to use without AccelStepper library.
/*
  #include "include/StepperDriver/DRV8834.h"
  #include "include/StepperDriver/DRV8834.cpp"
  #include "include/TimedAction/TimedAction.h"
  #include "include/TimedAction/TimedAction.cpp"
  #define MOTOR_STEPS 200 // Motor steps per revolution. Most steppers are 200 steps or 1.8 degrees/step
  #define MICROSTEPS 1 // Microstepping mode. If you hardwired it to save pins, set to the same value here.
  #define DIR 10
  #define STEP 11
  #define M0 12
  #define M1 13
  DRV8834 stepper(MOTOR_STEPS, DIR, STEP, M0, M1);
  // ^^ may need above code... test current code and uncomment if not working
*/


#define ACTUATOR_SIGNAL_PIN 6
Servo actuator;
AccelStepper stepper(AccelStepper::FULL4WIRE, 10, 11, 12, 13);
boolean previousExtendBool;
boolean extendBool = false;

void checkActuator(boolean current, boolean old) {
  if (old != current) {
    if (current == true) {
      actuator.writeMicroseconds(2000);
    } else {
      actuator.writeMicroseconds(1000);
    }
  }
}

// 1600 steps is a full revolution
void spinStepperMotor() {
  // Reset position to prevent integer overflow
  if (stepper.currentPosition() >= 32000)
  {
    //Serial.println(stepper.currentPosition());
    //Serial.println("Resetting position");
    stepper.setCurrentPosition(stepper.currentPosition() - 32000);

    // Need to reset max speed and acceleration when the position is reset
    stepper.setMaxSpeed(1000);
    stepper.setAcceleration(100);
  }
  stepper.moveTo(stepper.currentPosition() + 1600);

  //stepper.setSpeed(500);
  // ^ may be needed - experiment
}

void stopStepperMotor() {
  int currentPos = stepper.currentPosition();
  int stepsInRev = currentPos % 1600;
  int stepsToZero = 1600 - stepsInRev + 1600;
  int finalPos = currentPos + stepsToZero;
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

// When checking pressure reading, leave a gap between the condition change
// to prevent rapid switching on-off of the astrobio system during transition
// between ascent/descent and float.
void autoCollectionArm(float pressureReading) {
  if (pressureReading < 0.5) {
    previousExtendBool = extendBool;
    extendBool = true;
    checkActuator(extendBool, previousExtendBool);
    spinStepperMotor();
  } else if (pressureReading >= 1) {
    if (extendBool)
      stopStepperMotor();
    previousExtendBool = extendBool;
    extendBool = false;
    checkActuator(extendBool, previousExtendBool);
  }
}
