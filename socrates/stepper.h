#include <Arduino.h>
#define MOTOR_STEPS 200 // Motor steps per revolution. Most steppers are 200 steps or 1.8 degrees/step
#define MICROSTEPS 1 // Microstepping mode. If you hardwired it to save pins, set to the same value here.
#include "DRV8834.h"

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
