#include "autoCollectionArm.h"
#include "downlink.h"
#include "pwmSweep.h"

#define ASTROBIO_ON_BYTE1        0x11
#define ASTROBIO_ON_BYTE2        0x12
#define ASTROBIO_OFF_BYTE1       0x21
#define ASTROBIO_OFF_BYTE2       0x22
#define REBOOT_BYTE1             0x31
#define REBOOT_BYTE2             0x32
#define DOWNLINK_BYTE1           0x41
#define DOWNLINK_BYTE2           0x42
#define SWEEP_BYTE1              0x51
#define SWEEP_BYTE2              0x52

bool led = false;

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
    byte command[2];
    command[0] = Serial.read();
    delay(20);  // Wait for second byte
    command[1] = Serial.read();
    Serial.flush();

    // HASP command was received
    if (command[1] != 0)
    {
      // Turn on astrobiology system
      if (command[0] == ASTROBIO_ON_BYTE1 && command[1] == ASTROBIO_ON_BYTE2)//(command[0] == 'A')//
      {
        manualCommand = true;
        autoCollectionArm(0.1);  // Force the astrobio system to deploy
      }
      // Turn off astrobiology system
      else if (command[0] == ASTROBIO_OFF_BYTE1 && command[1] == ASTROBIO_OFF_BYTE2)//(command[0] == 'O')//
      {
        manualCommand = false;
        autoCollectionArm(2.0);  // Force the astrobio system to retract
      }
      // Force SOCRATES to reboot
      else if (command[0] == REBOOT_BYTE1 && command[1] == REBOOT_BYTE2)//(command[0] == 'R')//
      {
        // Force the astrobio system to close if we force a shut down of SOCRATES
        if (extendBool || manualCommand)
          autoCollectionArm(2.0);
        delay(15000);
        resetFunc();
      }
      else if (command[0] == DOWNLINK_BYTE1 && command[1] == DOWNLINK_BYTE2)//(command[0] == 'D')//
      {
        buildPacket();
      }
      // Perform the voltage sweep
      else if (command[0] == SWEEP_BYTE1 && command[1] == SWEEP_BYTE2)//(command[0] == 'P')//
      {
        if (led)
          digitalWrite(29, LOW);
        else
          digitalWrite(29, HIGH);
        led = !led;
        
        sweepAllCells();
      }
    }
  }
}
