#include <Arduino.h>
#include <Servo.h>


Servo actuator;
bool retract = false;
char groundCommand = 'C';


void setup() {
  actuator.attach(9); // change this val if actuator is not attached to pin 9
}

void loop() {
  if (Serial.available()) {
    groundCommand = Serial.read();
  }
  
  if(groundCommand== 'A'){
    retract = !retract;
  }
  if(retract == false){
      actuator.write(179);
  }else if(retract == true){
    actuator.write(50);
    }
    
  }
   
   
