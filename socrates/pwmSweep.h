//https://www.youtube.com/watch?v=YCjiIpZaGsc

#define pwmPin1 2
#define pwmPin2 3
#define pwmPin3 4
#define pwmPin4 5


// Sweeps one group of cells and prints to serial. Ends each cell with "\n"
void sweepPWMPin(int pinNum)
{
  float cell1Voltages[60];
  float cell2Voltages[60];
  float cell3Voltages[60];
  int var = 0;
  while (var < 60)
  {
    analogWrite(pinNum, var);
    // Read V0 for the three cells, save values to array
    var++;
    delay (10);  // ** May need to adjust this value **
  }

  // Send the data to the Pi
  for (int i = 0; i < 60; i++)
  {
    Serial.print(cell1Voltages[i]);
    Serial.print(",");
  }
  Serial.println();

  for (int i = 0; i < 60; i++)
  {
    Serial.print(cell2Voltages[i]);
    Serial.print(",");
  }
  Serial.println();

  for (int i = 0; i < 60; i++)
  {
    Serial.print(cell3Voltages[i]);
    Serial.print(",");
  }
  Serial.println();
}

// Performs the sweep
void sweepAllCells()
{
  Serial.print("begin_pwm");  // Signal for the Pi to store pwm values
  sweepPWMPin(pwmPin1);
  sweepPWMPin(pwmPin2);
  sweepPWMPin(pwmPin3);
  sweepPWMPin(pwmPin4);
  Serial.println("end_pwm");
}
