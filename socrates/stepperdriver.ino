
#include <Arduino.h>

// Motor steps per revolution. Most steppers are 200 steps or 1.8 degrees/step
#define MOTOR_STEPS 200

// Microstepping mode. If you hardwired it to save pins, set to the same value here.
#define MICROSTEPS 1

#define DIR 8
#define STEP 9
//#define SLEEP 13 // optional (just delete SLEEP from everywhere if not used)


#include "DRV8834.h"
#define M0 10
#define M1 11
DRV8834 stepper(MOTOR_STEPS, DIR, STEP, M0, M1);


// #include "BasicStepperDriver.h" // generic
// BasicStepperDriver stepper(DIR, STEP);

void setup() {
    /*
     * Set target motor RPM=12
     * rotates every 5 seconds!
     */
    stepper.begin(12, MICROSTEPS);

    // if using enable/disable on ENABLE pin (active LOW) instead of SLEEP uncomment next line
    // stepper.setEnableActiveState(LOW);
    stepper.enable();
}

void loop() {
    /*
     * The easy way is just tell the motor to rotate 360 degrees at 12rpm
     */
    stepper.rotate(360);
}
