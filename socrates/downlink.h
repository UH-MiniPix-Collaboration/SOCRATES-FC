// Used this for reference: https://forum.arduino.cc/index.php?topic=45282.0

#include "ambientPressure.h"
#include "issSensor.h"
#include "sampleThermistors.h"

#define NUM_DATA_INPUTS 40;  // Number of data inputs we have

int pNum = 0;  // Keep track of packet number

// Sample data packet
struct datapacket
{
  int packetNum;
  float ambPressure;
  float issPressure;  // In Pa
  float issTemperature;  // In *C
  float thermistors[14];
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

  for (int i = 0; i < 14; i++)
  {
    Serial.print(p.thermistors[i]);
    Serial.print(",");
  }

  for (int i = 0; i < 4; i++)
  {
    Serial.print(p.photodiodes[i]);
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
  //float* thermValues = readTempMux();
  for (int i = 0; i < 14; i++)
  {
    packet.thermistors[i] = 3.33; //thermValues[i];
  }

  // ** Call photodiode multiplexer here **
  //float* photoValues = readPhotoMux();
  for (int i = 0; i < 4; i++)
  {
    packet.photodiodes[i] = 432.7; //photoValues[i];
  }

  // Downlink the packet
  sendPacket(packet);
  pNum++;  // Increment packet number
}
