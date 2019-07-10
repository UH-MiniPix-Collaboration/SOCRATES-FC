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

  // Set up actuator
  actuator.attach(ACTUATOR_SIGNAL_PIN);
  delay(10);
  actuator.writeMicroseconds(1000);  // Ensure that the actuator starts retracted

  // Control pins for the Nano
  pinMode(NANO_POWER_PIN, OUTPUT);
  //digitalWrite(NANO_POWER_PIN, LOW);
  pinMode(NANO_SIGNAL_PIN, OUTPUT);
  //digitalWrite(NANO_SIGNAL_PIN, LOW);

  // Thermistor multiplexer pins
  pinMode(pinOut_S0, OUTPUT);
  pinMode(pinOut_S1, OUTPUT);
  pinMode(pinOut_S2, OUTPUT);

  // PWM sweep pins
  pinMode(pwmOutput, OUTPUT);

  // LED test pin
  pinMode(29, OUTPUT);
}
float ambpressure = 2.0;

void loop() {
  processCommands();
  if (manualCommand)
    autoCollectionArm(0.1);
  autoCollectionArm(ambpressure);  // getAmbientPressure()
  //int pin = analogRead(A2)* 4.9;
  //Serial.println(pin);
  //sweepAllCells();
  //delay(5000);
}
