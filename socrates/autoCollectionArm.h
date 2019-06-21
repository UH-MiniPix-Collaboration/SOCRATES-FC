#include <Arduino.h>
#include <Servo.h>
#include "DRV8834.h"

#define ACTUATOR_SIGNAL_PIN 6
#define MOTOR_STEPS 200 // Motor steps per revolution. Most steppers are 200 steps or 1.8 degrees/step
#define MICROSTEPS 1 // Microstepping mode. If you hardwired it to save pins, set to the same value here.
#define DIR 8
#define STEP 9
#define M0 10
#define M1 11

Servo actuator;
DRV8834 stepper(MOTOR_STEPS, DIR, STEP, M0, M1);

void autoCollectionArm(float pressureReading) {
  if (pressureReading < 0.5) {
    actuator.write(180);
    delay(1500); // give actuator time to extend before activating motor
    stepper.rotate(360);
  } else if (pressureReading >= 0.5) {
    stepper.move(-MOTOR_STEPS * MICROSTEPS);
    delay(1500);
    actuator.write(0);
  }
}
