#include <Arduino.h>
#include <Servo.h>
#include "include/StepperDriver/AccelStepper.h"
#include "include/StepperDriver/AccelStepper.cpp"
#include "include/StepperDriver/BasicStepperDriver.h"
#include "include/StepperDriver/BasicStepperDriver.cpp"

//#include "include/StepperDriver/DRV8834.h"
//#include "include/StepperDriver/DRV8834.cpp"
//#include "include/TimedAction/TimedAction.h"
//#include "include/TimedAction/TimedAction.cpp"

// Documentation for AccelStepper:
// http://www.airspayce.com/mikem/arduino/AccelStepper/classAccelStepper.html

//#define MOTOR_STEPS 200 // Motor steps per revolution. Most steppers are 200 steps or 1.8 degrees/step
//#define MICROSTEPS 1 // Microstepping mode. If you hardwired it to save pins, set to the same value here.
//#define DIR 7
//#define STEP 8
//#define M0 9
//#define M1 10
//DRV8834 stepper(MOTOR_STEPS, DIR, STEP, M0, M1);
// ^^ may need above code... test current code and uncomment if not working

#define ACTUATOR_SIGNAL_PIN 6
Servo actuator;
AccelStepper stepper(AccelStepper::FULL4WIRE, 7, 8, 9, 10);
boolean previousExtendBool;
boolean extendBool = False;
boolean actuatorState;

void checkActuator(boolean current, boolean old){
  if(old != current){
    if(current == True){
      actuator.writeMicroseconds(2000);
    }else{
      actuator.writeMicroseconds(1000);
    }
  }
}

void spinStepperMotor() {
  stepper.setMaxSpeed(500);
  stepper.setAcceleration(50);
  stepper.moveTo(360);
  //stepper.setSpeed(500);
  // ^ may be needed - experiment 
}

void stopStepperMotor() {
  stepper.setAcceleration(-50);
  stepper.moveTo(0);
  stepper.setSpeed(0);
}



void autoCollectionArm(float pressureReading) {
   if (pressureReading == 1){
     previousExtendBool = extendBool;
     extendBool = True;
     checkActuator(extendBool, previousExtendBool);
     spinStepperMotor();
     
   }else if (pressureReading == 0){
     stopStepperMotor();
     previousExtendBool = extendBool;
     extendBool == False;
     checkActuator(extendBool, previousExtendBool);
   }
}
