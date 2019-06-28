//https://www.youtube.com/watch?v=YCjiIpZaGsc

// Pin used to output the PWM voltage sweep
#define pwmOutput 8

// Analog pins to read in mux values
#define currentIn1 A2


// Sweeps one group of cells and prints to Pi. Ends each cell with "\n"
void sweepCellGroup()
{
  float cell1Currents[60];
  float cell2Currents[60];
  float cell3Currents[60];
  int var = 0;
  while (var < 60)
  {
    analogWrite(pwmOutput, var);
    delay(500);  // ** May need to adjust this value ** //

    // Read one group of cells, save values to arrays.
    // Currently reading one cell. Add mux reading for group.
    cell1Currents[var] = analogRead(currentIn1);
    
    var++;
  }
  analogWrite(pwmOutput, 0);  // Reset the PWM output to 0 V

  // Send the data to the Pi
  for (int i = 0; i < 60; i++)
  {
    Serial.print(cell1Currents[i]);
    Serial.print(",");
  }
  Serial.println();
  
  /*
      for (int i = 0; i < 60; i++)
      {
        Serial.print(cell2Currents[i]);
        Serial.print(",");
      }
      Serial.println();

      for (int i = 0; i < 60; i++)
      {
        Serial.print(cell3Currents[i]);
        Serial.print(",");
      }
      Serial.println();
  */
}

// ** TO DO ** //
sweepAllCells()
{
  // Sweep one group of cells then send data to Pi. Repeat for each cell group
}
