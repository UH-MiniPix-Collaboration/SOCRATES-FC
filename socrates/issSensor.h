#include <Wire.h>
#include <SPI.h>
#include "include/BMPLibrary/Adafruit_BMP280.h"
#include "include/BMPLibrary/Adafruit_BMP280.cpp"


Adafruit_BMP280 bmp; // I2C

float getISSTemperature()
{
    float issTemp = bmp.readTemperature();
    return issTemp;
}

float getISSPressure()
{
    float issPressure = bmp.readPressure();
    return issPressure;
}
