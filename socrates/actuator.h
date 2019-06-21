/*
#include <Arduino.h>
#include <Servo.h>

void extendActuator(){
  actuator.write(180);  // set to 141 for 30 mm actuator
}

void retractActuator(){
   actuator.write(0);  // set to 81 for 30 mm actuator
}

// Test the actuator by cycling between maximum and minimum extension
void testCycle()
{
  int pos;
  for (pos = 0; pos <= 180; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    actuator.write(pos);              // tell servo to go to position in variable 'pos'
    delay(30);                       // waits 15ms for the servo to reach the position
  }
  for (pos = 180; pos >= 0; pos -= 1) { // goes from 180 degrees to 0 degrees
    actuator.write(pos);              // tell servo to go to position in variable 'pos'
    delay(30);                       // waits 15ms for the servo to reach the position
  }
}
*/
