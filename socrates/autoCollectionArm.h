#include <Arduino.h>
#include <Servo.h>
#include "DRV8834.h"

#include <TimedAction.h>
//NOTE: This library has an issue on newer versions of Arduino. After
//      downloading the library you MUST go into the library directory and
//      edit TimedAction.h. Within, overwrite WProgram.h with Arduino.h

#define ACTUATOR_SIGNAL_PIN 6
#define MOTOR_STEPS 200 // Motor steps per revolution. Most steppers are 200 steps or 1.8 degrees/step
#define MICROSTEPS 1 // Microstepping mode. If you hardwired it to save pins, set to the same value here.
#define DIR 8
#define STEP 9
#define M0 10
#define M1 11
Servo actuator;
DRV8834 stepper(MOTOR_STEPS, DIR, STEP, M0, M1);

void spinStepper(){
  stepper.rotate(360);
}

void stopStepper(){
  stepper.move(-MOTOR_STEPS * MICROSTEPS);
}

TimedAction spinStepper = TimedAction(300,spinStepper);
TimedAction stopStepper = TimedAction(300,stopStepper);

void autoCollectionArm(float pressureReading) {
  if (pressureReading < 0.5) {
    spinStepper.check();
  } else if (pressureReading >= 0.5) {
    stopStepper.check();
  }
}
