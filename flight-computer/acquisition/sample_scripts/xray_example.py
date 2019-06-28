def getFirstXray():
    xrays = pixet.devicesByType(pixet.PX_DEVTYPE_XRAY)
    if not xrays:
        print "Not XRay tube found"
    xray = xrays[0]
    return xray


# -----------------------------------------------------------------------------------
#                                   XRAY CONTROL
# -----------------------------------------------------------------------------------
def xrayExample():
    xray = getFirstXray()
    print xray.fullName() # device name
    xray.setVoltage(100) # set 100 kV voltage
    xray.setCurrent(60) # set 60 uA current
    xray.turnXrayOn() # turn on Xray
    xray.turnXrayOff() # turn off Xray

    print xray.voltage() # current tube voltage
    print xray.current() # current tube current
    print xray.temperature() # current tube temperature
    print xray.minVoltage() # minimum possible voltage to set
    print xray.minCurrent() # minimum possible current to set
    print xray.maxVoltage() # maximum possible voltage to set
    print xray.maxCurrent() # maximum possible current to set
    print xray.isInterlockOn() # is interlock closed 


# -----------------------------------------------------------------------------------
#                                       MAIN
# -----------------------------------------------------------------------------------

#xrayExample()
