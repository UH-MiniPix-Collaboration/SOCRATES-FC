#include "actuator.h"

#define actuatorPin 6
#define motorPin 7
#define ACTUATOR_BYTE1        0x11
#define ACTUATOR_BYTE2        0x12
#define MOTOR_BYTE1           0x21
#define MOTOR_BYTE2           0x22

bool aState = false;
bool mState = false;

void processCommands()
{
  // Read the serial input
  int numIncomingBytes = Serial.available();
  if (numIncomingBytes > 0)
  {
    byte command[numIncomingBytes];
    for (int i = 0; i < numIncomingBytes; i++)
    {
      byte incomingByte = Serial.read();
      command[i] = incomingByte;
    }
    Serial.flush();
    if (command[0] == ACTUATOR_BYTE1 && command[1] == ACTUATOR_BYTE2)
    {
      aState = !aState;
      if (aState)
      {
        digitalWrite(6, HIGH);
        extendActuator();
      }
      else
      {
        digitalWrite(6, LOW);
        retractActuator();
      }
    }
    else if (command[0] == MOTOR_BYTE1 && command[1] == MOTOR_BYTE2)
    {
      mState = !mState;
      if (mState)
        digitalWrite(7, HIGH);
      else
        digitalWrite(7, LOW);
    }
  }
}
