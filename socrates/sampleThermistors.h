// Last updated 3:00pm June 15, 2019

// multiplexers http://www.ti.com/lit/ds/symlink/cd74hc4051.pdf
// thermistors https://learn.adafruit.com/thermistor/using-a-thermistor

// definitions and variabls for temperature sensing
#define NUMSAMPLES 4 // number of samples for average
#define THERMISTORNOMINAL 10000 // resistance at 25 deg. C
#define TEMPERATURENOMINAL 25 // temp. for nominal resistance
#define BCOEFFICIENT 3950 // beta coefficient of thermistor (3000-4000)
#define SERIESRESISTOR 10000 // "other" resistance "seen" by thermistor
#define SENSORCOUNT 7
int index = 0; // muxState[] index
float average; // average value of N samples
float steinhart;
int samples[NUMSAMPLES]; //mux0 8 thermistors


// multiplexer variables
// These pin numbers might be wrong; might need to change the numbers here
#define pinOut_S0 47 // IC pin 11, digital select
#define pinOut_S1 49 // IC pin 10, digital select
#define pinOut_S2 51 // IC pin 9, digital select
#define pinInMux0 A0 // mux0 pin 3, analog read
float muxState[SENSORCOUNT] = {0}; // to hold temps
//int sensorValue = 0;
int muxSelect = 0; //used to increment through muxes

void convertToTemp()
{
  // convert the value to resistance by steinhart equation
  average = 1023 / average - 1;
  average = SERIESRESISTOR / average;
  steinhart = average / THERMISTORNOMINAL;     // (R/Ro)
  steinhart = log(steinhart);                  // ln(R/Ro)
  steinhart /= BCOEFFICIENT;                   // 1/B * ln(R/Ro)
  steinhart += 1.0 / (TEMPERATURENOMINAL + 273.15); // + (1/To)
  steinhart = 1.0 / steinhart;                 // Invert
  steinhart -= 273.15;                         // convert to C
  if (steinhart == -273.15) // if zero make it zero.
    steinhart = 0.0;

  muxState[index] = steinhart;
  //Serial.print(muxState[index]);
  //Serial.print(",");
  /* //Debug serial monitor
    Serial.print("Temperature ");
    Serial.print(steinhart);
    Serial.print(muxState[count]);
    Serial.println(" *C");*/
  if (index < SENSORCOUNT) // increment counter tracking sensor number
    index++; //
  else
  {
    //Serial.println("count reset"); //Debug serial monitor
    index = 0; //
  }
  delay(1);
}

void updateTemperatureMux()
{
  for (int i = 0; i <= SENSORCOUNT; i++) // mux input counter
  {
    for (int j = 0; j < NUMSAMPLES; j++) // take N samples
    {
      // Pins S0,S1,S2 select the mux pin by logically ANDing
      // the bit-wise ANDed mux input counter.
      digitalWrite(pinOut_S0, HIGH && (i & B00000001));
      digitalWrite(pinOut_S1, HIGH && (i & B00000010));
      digitalWrite(pinOut_S2, HIGH && (i & B00000100));
      delay(10);
      samples[j] = analogRead(pinInMux0);
      //Serial.print(samples[j]);
      //Serial.println(",");
      /*
        switch(muxSelect)
        {
          case 0:
          samples[j] = analogRead(pinInMux0);
          break;
          case 1:
          samples[j] = analogRead(pinInMux1);
          break;
        }
      */
      /*Commented out to test the switch-case above.
        if(muxSelect == 0)
        {
        samples[j] = analogRead(pinInMux0); //store mux0 sample values
        }
        if(muxSelect == 1)
        {
        samples[j] = analogRead(pinInMux1); //store mux1 sample values
        }*/

      delay(10);
    }
    average = 0; //clear average accumulator
    for (int k = 0; k < NUMSAMPLES; k++)
    {
      average += samples[k]; // accumulate samples
    }
    average /= NUMSAMPLES; //final sample average
    convertToTemp(); //conversion to temperature value
    delay(10);
  }
}

float* readTempMux()
{
  //Serial.println("Reading Mux0"); //Debug serial monitor
  muxSelect = 0; //Select mux0
  updateTemperatureMux(); //Sample mux0 pins
  /*
    //Debug serial monitor loop
    for (int i = 0; i < SENSORCOUNT; i++)
    {
    Serial.print(muxState[i]);
    Serial.print(" ");
    delay(10);
    }
    Serial.print("Looping\n");
    delay(10);
  */

  return muxState;
}
