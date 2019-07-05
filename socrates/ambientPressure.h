#include <Wire.h>
#include "include/MS5803Library/SparkFun_MS5803_I2C.h"
#include "include/MS5803Library/SparkFun_MS5803_I2C.cpp"


// Pins D20 and D21

//  ADDRESS_HIGH = 0x76
MS5803 sensor(ADDRESS_HIGH);

float getAmbientPressure()
{
  return sensor.getPressure(ADC_4096);
}
