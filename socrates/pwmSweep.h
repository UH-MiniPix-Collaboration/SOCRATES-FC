//https://www.youtube.com/watch?v=YCjiIpZaGsc
//http://www.learningaboutelectronics.com/Articles/MCP4131-digital-potentiometer-circuit.php

#include <SPI.h>


byte digipotAddress = 0x00;  // The address of the digipot
int CS = 53;

// 10 -> 53
// 11 -> 51
// 13 -> 52

// Pin used to output the PWM voltage sweep
//#define pwmOutput 7

// Analog pins to read in current values
#define negativeCurrentIn1 A2
#define positiveCurrentIn1 A1

#define currentIn2 A3
#define digipotOut A4

#define digiPotPower 25

#define NUM_SAMPLES 3

// Write a value to the digipot terminal
int digitalPotWrite(int value)
{
  digitalWrite(CS, LOW);
  SPI.transfer(digipotAddress);
  SPI.transfer(value);
  digitalWrite(CS, HIGH);
}

// Sweeps one group of cells and prints to Pi. Ends each cell with "\n"
void sweepCellGroup(int groupNum)
{
  // All arrays store voltages in MILLIVOLTS
  float digipotOutput[129] = {0};
  float negativeCell1Currents[129] = {0};
  float positiveCell1Currents[129] = {0};

  float cell2Currents[129];

  digitalWrite(digiPotPower, HIGH);
  digitalPotWrite(0);

  // Sweep voltages and collect readings
  for (int i = 0; i <= 128; i++)
  {
    //Serial.println(i);
    digitalPotWrite(i);
    delay(10);
    for (int j = 0; j < NUM_SAMPLES; j++)
    { 
      digipotOutput[i] += (analogRead(digipotOut) * 5000.0 / 1024.0);
      negativeCell1Currents[i] += (analogRead(negativeCurrentIn1) * 5000.0 / 1024.0);
      positiveCell1Currents[i] += (analogRead(positiveCurrentIn1) * 5000.0 / 1024.0);
      delay(10);
    }

  }
  digitalPotWrite(0);
  digitalWrite(digiPotPower, LOW);
  delay(10);


  // Send the data to the Pi
  Serial.print("begin_pwm,");
  Serial.print(groupNum);
  Serial.print(",");
  for (int i = 0; i <= 128; i++)
  {
    Serial.print(digipotOutput[i]/NUM_SAMPLES);
    Serial.print(";");
    Serial.print(negativeCell1Currents[i]/NUM_SAMPLES);
    Serial.print(";");
    Serial.print(positiveCell1Currents[i]/NUM_SAMPLES);
    Serial.print(",");
  }
  digitalPotWrite(0);
  /*
    Serial.print("begin_pwm,");
    Serial.print(groupNum+1);
    Serial.print(",");
    for (int i = 0; i <= 128; i++)
    {
    Serial.print(digipotOutput[i]);
    Serial.print(";");
    Serial.print(cell1Currents[i]);
    Serial.print(",");
    }
  */
  Serial.println();  // End each cell group with a newline
  delay(100);
}

// ** TO DO ** //
sweepAllCells()
{
  // Sweep one group of cells then send data to Pi. Repeat for each cell group
  for (int i = 1; i < 2; i += 2)
  {
    sweepCellGroup(i);
  }
}
