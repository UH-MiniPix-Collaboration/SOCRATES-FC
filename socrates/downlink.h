// Used this for reference: https://forum.arduino.cc/index.php?topic=45282.0

#include "ambientPressure.h"
#include "issSensor.h"
#include "sampleThermistors.h"


#define NUM_THERMISTORS 8
#define NUM_PHOTODIODES 4


long pNum = 1;  // Keep track of packet number

// Sample data packet
struct datapacket
{
  long packetNum;
  float ambPressure;
  float issPressure;  // In Pa
  float issTemperature;  // In *C
  float thermistors[8];  // In *C
  float photodiodes[4];
};


// **********TODO**********
// Sends pre-compiled data to the serial port
void sendPacket(datapacket p)
{
  unsigned long bufferSize = sizeof(datapacket);  // Returns number of bytes

  Serial.print(p.packetNum);
  Serial.print(",");

  Serial.print(p.ambPressure);
  Serial.print(",");

  Serial.print(p.issPressure);
  Serial.print(",");

  Serial.print(p.issTemperature);
  Serial.print(",");

  for (int i = 0; i < NUM_THERMISTORS; i++)
  {
    Serial.print(p.thermistors[i]);
    Serial.print(",");
  }

  for (int i = 0; i < NUM_PHOTODIODES; i++)
  {
    Serial.print(p.photodiodes[i]);
    if (i != (NUM_PHOTODIODES - 1) )
      Serial.print(",");
  }

  Serial.println();  // End the packet with \n
  Serial.flush();
}

// **********TODO**********
void buildPacket()
{
  // Read through each data input pin; add each data value to the struct
  datapacket packet;
  packet.packetNum = pNum;
  packet.ambPressure = getAmbientPressure();
  packet.issPressure = getISSPressure();
  packet.issTemperature = getISSTemperature();

  // ** Call temperature multiplexers here **
  //Serial.println("Calling mux");  // Used for debugging; comment out for final build
  float* thermValues = readTempMux();
  for (int i = 0; i < NUM_THERMISTORS; i++)
  {
    packet.thermistors[i] = thermValues[i]; //packet.thermistors[i] = 3.33; //
  }

  // ** Call photodiode pins here **
  for (int i = 0; i < NUM_PHOTODIODES; i++)
  {
    packet.photodiodes[i] = 432.7; //photoValues[i];
  }

  // Downlink the packet
  sendPacket(packet);
  pNum++;
}
