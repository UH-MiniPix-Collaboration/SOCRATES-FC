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
  float thermistors[14];
    float cellVoltages[12];
    float cellCurrents[12];
    float ambPressure;
  // ... add variables for remaining data values ...
};

// **********TODO**********
void sendPacket(datapacket p)
{
  unsigned long bufferSize = sizeof(datapacket);  // Returns number of bytes

  Serial.print(p.packetNum);
  Serial.print(",");

  for (int i = 0; i < 14; i++)
  {
    Serial.print(p.thermistors[i]);
    Serial.print(",");
  }

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

  Serial.print(p.ambPressure);
  Serial.print(",");

  Serial.println();  // End the packet with \n
  Serial.flush();
}

// **********TODO**********
void buildPacket()
{
  // Read through each data input pin; add each data value to the struct
  datapacket packet;
  packet.packetNum = num;

  p.ambPressure = getAmbientPressure();

  // ** Call multiplexers here **
  //float* thermValues = readMux();

  // Downlink the packet
  sendPacket(packet);
  num++;
}
