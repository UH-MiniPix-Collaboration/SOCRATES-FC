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
  actuator.attach(ACTUATOR_SIGNAL_PIN);
  delay(10);
  actuator.writeMicroseconds(1000);  // Ensure that the actuator starts retracted

  // Thermistor multiplexer pins
  pinMode(pinOut_S0, OUTPUT);
  pinMode(pinOut_S1, OUTPUT);
  pinMode(pinOut_S2, OUTPUT);

  // PWM sweep pins
  pinMode(pwmPin1, OUTPUT);
  pinMode(pwmPin2, OUTPUT);
  pinMode(pwmPin3, OUTPUT);
  pinMode(pwmPin4, OUTPUT);

  // LED test pin
  pinMode(52, OUTPUT);
}

void loop() {
  processCommands();
  //buildPacket();
  //autoCollectionArm(getAmbPressure());
  //delay(1000);
}
