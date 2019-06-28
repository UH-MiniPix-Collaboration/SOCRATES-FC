def motorByName(name):
    # returns the motor object by it's name
    motors = pixet.devicesByType(pixet.PX_DEVTYPE_MOTOR)
    motor = None
    for m in motors:
        if m.motorName() == name:
            return m
    return None


# -----------------------------------------------------------------------------------
#                      Motor Functions
# -----------------------------------------------------------------------------------
def motorFunctions():
    motor = motorByName("rotation")
    print motor.fullName()
    print motor.motorName()
    print motor.deviceStatusText() # status of the motor
    print motor.isRunning() # is motor moving
    motor.stop() # stop motor movement
    motor.setZero() # zero the position counter
    print motor.position() # current motor position


# -----------------------------------------------------------------------------------
#                      Move motor to absolute position
# -----------------------------------------------------------------------------------
def motorExample1():
    motor = motorByName("rotation")
    destination = 10
    waitForMoveToFinish = True
    rc = motor.moveAbsolute(destination, waitForMoveToFinish)
    print "Move motor: %d" % rc

# -----------------------------------------------------------------------------------
#                      Move motor relative to current position
# -----------------------------------------------------------------------------------
def motorExample1():
    motor = motorByName("rotation")
    destination = -10 # moves to position - 10 units
    waitForMoveToFinish = True
    rc = motor.moveRelative(destination, waitForMoveToFinish)
    print "Move motor: %d" % rc


# -----------------------------------------------------------------------------------
#                                 MAIN
# -----------------------------------------------------------------------------------
#motorFunctions()
#motorExample1()
#motorExample2()
