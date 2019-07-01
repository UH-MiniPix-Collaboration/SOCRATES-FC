#include "uplink.h"
//#include "downlink.h"

#define baudRate 4800


void setup() {
  Serial.begin(baudRate);

  // ISS sensor: default settings from datasheet
  bmp.begin();
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     /* Operating Mode. */
                  Adafruit_BMP280::SAMPLING_X2,     /* Temp. oversampling */
                  Adafruit_BMP280::SAMPLING_X16,    /* Pressure oversampling */
                  Adafruit_BMP280::FILTER_X16,      /* Filtering. */
                  Adafruit_BMP280::STANDBY_MS_500); /* Standby time. */

  // Set up servos
  stepper.setCurrentPosition(0);
  stepper.setMaxSpeed(4000);
  stepper.setAcceleration(100);
  actuator.attach(ACTUATOR_SIGNAL_PIN);
  delay(10);
  actuator.writeMicroseconds(1000);  // Ensure that the actuator starts retracted

  // Thermistor multiplexer pins
  pinMode(pinOut_S0, OUTPUT);
  pinMode(pinOut_S1, OUTPUT);
  pinMode(pinOut_S2, OUTPUT);

  // PWM sweep pins
  pinMode(pwmOutput, OUTPUT);

  // LED test pin
  pinMode(52, OUTPUT);
  pinMode(30, INPUT);
  pinMode(32, INPUT);
}
float ambPressure = 1;

void loop() {
  processCommands();
  if (manualCommand)
    autoCollectionArm(0);
  //autoCollectionArm(0);
  //buildPacket();
  /*
  if (digitalRead(30) == LOW)
    ambPressure = 0.1;
  if (digitalRead(32) == LOW)
    ambPressure = 1;
  autoCollectionArm(ambPressure);
  */
  stepper.run();
}
