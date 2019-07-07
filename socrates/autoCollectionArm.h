#include <Arduino.h>
#include <Servo.h>


#define ACTUATOR_SIGNAL_PIN 6
#define NANO_POWER_PIN 2
#define NANO_SIGNAL_PIN 3

Servo actuator;
boolean previousExtendBool;
boolean extendBool = false;
boolean motorActivated = false;
boolean manualCommand = false;  // Control whether the system was activated manually
bool led = false;  // Used for testing. Remove later.

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
  if (!motorActivated)
  {
    digitalWrite(NANO_POWER_PIN, HIGH);
    motorActivated = true;
  }
}

void stopStepperMotor() {
  digitalWrite(NANO_SIGNAL_PIN, HIGH);
  delay(15000);  // Wait for motor to return to home position. We can look into protothreading this
  digitalWrite(NANO_POWER_PIN, LOW);
  digitalWrite(NANO_SIGNAL_PIN, LOW);
  motorActivated = false;
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
  } else if (pressureReading >= 1.0) {
    if (extendBool)
      stopStepperMotor();
    previousExtendBool = extendBool;
    extendBool = false;
    manualCommand = false;
    checkActuator(extendBool, previousExtendBool);
  }
}
