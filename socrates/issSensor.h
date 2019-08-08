#include <Wire.h>
#include <SPI.h>
#include "include/BMPLibrary/Adafruit_Sensor.h"
#include "include/BMPLibrary/Adafruit_BMP280.h"
#include "include/BMPLibrary/Adafruit_BMP280.cpp"


#define BMP_SCK  (13)
#define BMP_MISO (12)
#define BMP_MOSI (11)
#define BMP_CS   (10)
Adafruit_BMP280 bmp(BMP_CS, BMP_MOSI, BMP_MISO,  BMP_SCK);


float getISSPressure()
{
  return bmp.readPressure();
}

float getISSTemperature()
{
  return bmp.readTemperature();
}
