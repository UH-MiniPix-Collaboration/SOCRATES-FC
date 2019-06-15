#include <Arduino.h>
#include <Servo.h>

Servo actuator;
void setup(){
  actuator.attach(6); // change this val if actuator is not attached to pin 6
}

void extendActuator(){
  actuator.write(179);
}

void retractActuator(){
   actuator.write(50);
}
   
