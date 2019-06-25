#include "autoCollectionArm.h"
#include "pwmSweep.h"

#define ASTROBIO_ON_BYTE1        0x11
#define ASTROBIO_ON_BYTE2        0x12
#define ASTROBIO_OFF_BYTE1       0x21
#define ASTROBIO_OFF_BYTE2       0x22
#define REBOOT_BYTE1             0x31
#define REBOOT_BYTE2             0x32
#define PWM_BYTE1                0x41
#define PWM_BYTE2                0x41


// https://www.instructables.com/id/two-ways-to-reset-arduino-in-software/
// Restarts the Arduino
void(* resetFunc) (void) = 0; //declare reset function @ address 0

// Handles all HASP commands sent from the RPi as well as the internal command of pwm sweeping
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

    // HASP command was received
    if (numIncomingBytes == 2)
    {
      // Turn on astrobiology system
      if (command[0] == ASTROBIO_ON_BYTE1 && command[1] == ASTROBIO_ON_BYTE2)
      {
        autoCollectionArm(0);
      }
      else if (command[0] == ASTROBIO_OFF_BYTE1 && command[1] == ASTROBIO_OFF_BYTE2)
      {
        autoCollectionArm(1);
      }
      else if (command[0] == REBOOT_BYTE1 && command[1] == REBOOT_BYTE2)
      {
        resetFunc();
      }
      else if (command[0] == PWM_BYTE1 && command[1] == PWM_BYTE2)
      {
        sweepAllCells();
      }
    }
  }
}
