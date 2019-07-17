#include <Wire.h>
#include "include/MS5803Library/SparkFun_MS5803_I2C.h"
#include "include/MS5803Library/SparkFun_MS5803_I2C.cpp"


// https://forum.arduino.cc/index.php?topic=289441.0


// Pins D20 and D21

//  ADDRESS_HIGH = 0x76
MS5803 ambSensor(ADDRESS_HIGH);

float getAmbientPressure()
{
  // Might need this
  pinMode(21, OUTPUT);
  for (int i = 0; i < 8; i++) {
    digitalWrite(21, HIGH);
    delayMicroseconds(3);
    digitalWrite(21, LOW);
    delayMicroseconds(3);
  }
  pinMode(21, INPUT);

  return ambSensor.getPressure(ADC_4096);
}
