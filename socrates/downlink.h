// Used this for reference: https://forum.arduino.cc/index.php?topic=45282.0

#include "multiplexers.h"
#include "pressureSensor.h"

#define NUM_DATA_INPUTS 40;  // Number of data inputs we have

int num = 0;

// Sample data packet
struct datapacket
{
  //unsigned char byteArray[NUM_DATA_INPUTS];
  int packetNum;
  float thermistors[12];
  float cellVoltages[12];
  float cellCurrents[12];
  float ambPressure;
  // ... add variables for remaining data values ...
};

// **********TODO**********
void sendPacket(datapacket p)
{
  unsigned long bufferSize = sizeof(datapacket);  // Returns number of bytes
  p.packetNum = num;
  Serial.print(p.packetNum);
  Serial.print(",");
  /*
  for (int i = 0; i < 12; i++)
    p.thermistors[i] = i*num;
  for (int i = 0; i < 12; i++)
  {
    Serial.print(p.thermistors[i]);
    Serial.print(",");
  }
  */
  p.ambPressure = getAmbientPressure();
  Serial.print(p.ambPressure);
  Serial.print(",");
  Serial.println();

  /*
    for (int i = 0; i < 12; i++)
    {
    Serial.print(p.cellVoltages[i]);
    Serial.print(",");
    }

    for (int i = 0; i < 12; i++)
    {
    Serial.print(p.cellCurrents[i]);
    Serial.print(",");
    }
  */

  // Copy the data in the struct into a char array to be sent via serial
  /*
    char pBuffer[bufferSize];
    memcpy(pBuffer, &p, bufferSize);  // Copies the *bytes* from p into pBuffer (data types are irrelevant)

    // Send each data value through the serial connection
    for (int i = 0; i < bufferSize; i++)
    {
    //Serial.print("pBuffer[i]: ");
    //Serial.println(pBuffer[i]);
    //Serial.println(p.header);
    Serial.write(pBuffer[i]);
    }
  */
  Serial.flush();
}

// **********TODO**********
void buildPacket()
{
  // Read through each data input pin
  // Add each data value to the struct
  datapacket packet;

  // To add the thermistor values, call the multiplexers
  // ** Call multiplexers here **
  //float* thermValues = readMux();
  // Downlink the packet
  sendPacket(packet);
  num++;
}
