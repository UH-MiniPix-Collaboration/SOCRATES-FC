// Last updated 3:00pm June 15, 2019

// multiplexers http://www.ti.com/lit/ds/symlink/cd74hc4051.pdf
// thermistors https://learn.adafruit.com/thermistor/using-a-thermistor

// definitions and variabls for temperature sensing
#define NUMSAMPLES 10 // number of samples for average
#define THERMISTORNOMINAL 10000 // resistance at 25 deg. C
#define TEMPERATURENOMINAL 25 // temp. for nominal resistance
#define BCOEFFICIENT 3950 // beta coefficient of thermistor (3000-4000)
#define SERIESRESISTOR 10000 // "other" resistance "seen" by thermistor
#define SENSORCOUNT 15
int index = 0; // muxState[] index
float average; // average value of N samples
float steinhart;
int samples[NUMSAMPLES]; //mux0 8 thermistors


// multiplexer variables
#define pinOut_S0 2 // IC pin 11, digital select
#define pinOut_S1 3 // IC pin 10, digital select
#define pinOut_S2 4 // IC pin 9, digital select
#define pinInMux0 A0 // mux0 pin 3, analog read
#define pinInMux1 A1 // mux1 pin 3, analog read
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
  /* //Debug serial monitor
  Serial.print("Temperature "); 
  Serial.print(steinhart);
  Serial.print(muxState[count]);
  Serial.println(" *C");*/
  if(index<SENSORCOUNT) // increment counter tracking sensor number
    index++; //
  else
  {
    //Serial.println("count reset"); //Debug serial monitor
    index = 0; //
  }
  delay(10);
}

void updateTemperatureMux()
{
  for(int i = 0; i < 8; i++) // mux input counter
  {
    for(int j=0; j < NUMSAMPLES; j++) // take N samples
    {
      // Pins S0,S1,S2 select the mux pin by logically ANDing
      // the bit-wise ANDed mux input counter.
      digitalWrite(pinOut_S0, HIGH && (i & B00000001));
      digitalWrite(pinOut_S1, HIGH && (i & B00000010));
      digitalWrite(pinOut_S2, HIGH && (i & B00000100));

      switch(muxSelect)
      {
        case 0:
        samples[j] = analogRead(pinInMux0);
        break;
        case 1:
        samples[j] = analogRead(pinInMux1);
        break;
      }
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
    for(int j=0; j<NUMSAMPLES; j++)
    {
      average += samples[j]; // accumulate samples
    }
    average /= NUMSAMPLES; //final sample average
    convertToTemp(); //conversion to temperature value
    delay(10);
  }
}

float* readMux()
{
  //Serial.println("Reading Mux0"); //Debug serial monitor
  muxSelect = 0; //Select mux0
  updateTemperatureMux(); //Sample mux0 pins
  //Serial.println("Reading Mux1"); //Debug serial monitor
  muxSelect = 1; //Select mux1
  updateTemperatureMux(); //Sample mux1 pins
  return muxState;
  /* //Debug serial monitor loop
  for (int i = 0; i <= SENSORCOUNT; i++)
  {
    Serial.print(muxState[i]);
    Serial.print(" ");
    delay(10);
  }
  Serial.print("Looping\n");
  delay(10);*/
}
