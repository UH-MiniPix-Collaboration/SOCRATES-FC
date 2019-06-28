def getFirstHvSource():
    hvs = pixet.devicesByType(pixet.PX_DEVTYPE_HVSOURCE)
    if not hvs:
        print "Not HV Source unit found"
    hv = hvs[0]
    return hv


# -----------------------------------------------------------------------------------
#                                   HV CONTROL
# -----------------------------------------------------------------------------------
def hvExample():
    hv = getFirstHvSource()
    print hv.fullName() # device name

    index = 0 # 0 = positive, 1 = negative
    hv.setVoltage(index, 100) # set 100 V

    print hv.voltage() # current set voltage
    print hv.voltageSense()  # sense of the hv voltage (V)
    print hv.currentSense()  # sense of the hv source current (uA)
    print hv.minVoltage()  # min voltage possile to set
    print hv.maxVoltage()  # max voltage possile to set


# -----------------------------------------------------------------------------------
#                                       MAIN
# -----------------------------------------------------------------------------------
#hvExample()
