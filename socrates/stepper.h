#include <Arduino.h>
#define MOTOR_STEPS 200 // Motor steps per revolution. Most steppers are 200 steps or 1.8 degrees/step
#define MICROSTEPS 1 // Microstepping mode. If you hardwired it to save pins, set to the same value here.
#define DIR 8
#define STEP 9
#include "DRV8834.h"
#define M0 10
#define M1 11
DRV8834 stepper(MOTOR_STEPS, DIR, STEP, M0, M1);

void setup() {
  stepper.begin(12, MICROSTEPS); // sets motor to RPM=12
  stepper.enable();
}

void spinStepper() {
  //stepper.enable();
  stepper.rotate(360);
}

void stopStepper(){
  stepper.move(-MOTOR_STEPS*MICROSTEPS);
  //stepper.disable();
}

// may want to change some things - need to experiment with motor
// implimenting sleep or disable may reduce energy used
