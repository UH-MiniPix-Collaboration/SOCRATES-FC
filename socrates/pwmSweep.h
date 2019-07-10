//https://www.youtube.com/watch?v=YCjiIpZaGsc

// Pin used to output the PWM voltage sweep
#define pwmOutput 7

// Analog pins to read in current values
#define currentIn1 A2
#define currentIn2 A3


// Sweeps one group of cells and prints to Pi. Ends each cell with "\n"
void sweepCellGroup(int groupNum)
{
  float cell1Currents[60];
  float cell2Currents[60];
  /*
    for (int var = 0; var < 60; var++)
    {
    analogWrite(pwmOutput, var);
    delay(100);  // ** May need to adjust this value ** //

    // Read one group of cells, save values to arrays.
    cell1Currents[var] = analogRead(currentIn1);
    cell2Currents[var] = analogRead(currentIn2);
    }
    analogWrite(pwmOutput, 1);  // Reset the PWM output to 0 V
  */
  digitalWrite(pwmOutput, HIGH);

  while (true)
  {
    Serial.print(analogRead(currentIn1) * 5.0 / 1024.0); // This currently outputs VOLTS. Divide by 10,000 to get amperage
    Serial.println(",");
    delay(100);
  }

  // Send the data to the Pi
  Serial.print("begin_pwm,");
  Serial.print(groupNum);
  Serial.print(",");
  for (int i = 0; i < 60; i++)
  {
    Serial.print(i * 5.0 / 255.0);
    Serial.print(",");
    Serial.print(cell1Currents[i]);
    Serial.println(",");
  }
  /*
    Serial.print("begin_pwm,");
    Serial.print(groupNum + 1);
    Serial.print(",");
    for (int i = 0; i < 60; i++)
    {
    Serial.print(cell2Currents[i]);
    if (i != 59)
      Serial.print(",");
    }
  */
  Serial.println();
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
