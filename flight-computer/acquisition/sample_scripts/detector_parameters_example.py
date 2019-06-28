# first list all Medipix/Timepix devices and use the first one:
devices = pixet.devicesByType(pixet.PX_DEVTYPE_MPX2)
if not devices:
    raise "No devices connected"
device = devices[0] # use  the first device

# -----------------------------------------------------------------------------------
#                      DETECTOR INFORMATION
# -----------------------------------------------------------------------------------
def detExample0():
    print device.fullName()
    print device.width()
    print device.heigth()
    print device.pixelCount()
    print device.chipCount()
    print device.chipIDs() # list of detector chip IDs

# -----------------------------------------------------------------------------------
#                      DETECTOR CONFIG
# -----------------------------------------------------------------------------------
def detExample1():
    device.saveConfigToFile("somefile.xml")
    device.loadConfigFromFile("somefile.xml")
    device.loadFactorConfig() # loads factory config from factory dir, if exists
    print device.hasDefaultConfig() # if device has no config

# -----------------------------------------------------------------------------------
#                       RAW DAC CONTROL Example
# -----------------------------------------------------------------------------------
def detExample2():
    dacs = device.dacs()
    print dac.count() # number of DAC parameters (all chips)
    print dac.singleChipCount() # number of DAC of sinlge chip

    dacs.setDac(pixet.PX_TPX_IKRUM, 0, 20) # sets the IKRUM DAC of chip 0 to value 20
    dacs.setDac(pixet.PX_TPX_IKRUM, pixet.PX_MPXDACS_CHIP_ALL, 20) # sets the IKRUM DAC of all chips to value 20
    dacs.dac(pixet.PX_TPX_IKRUM, 0) # get the set value of the IKRUM DAC of chip 0
    print dacs.maxValue(pixet.PX_TPX_THLFINE) # get the maximum possible value of thl fine dac

    dacs.analogDac(pixet.PX_TPX_THLFINE, 0, 1) # get analog value of Thl fine dac of chip 0. Do the sense only once (1)

    dacs.setDefault() # set defaults dac values


# -----------------------------------------------------------------------------------
#                      ENERGY THRESHOLD 
# -----------------------------------------------------------------------------------
def detExample3():
    # setTheshold function flags:
    # pixet.PX_THLFLAG_NONE - sets the raw dac value of threshold 
    # pixet.PX_THLFLAG_RELATIVE - change the threshold relative to current value (e.g. for value 5, it would add 5 to threshold)
    # pixet.PX_THLFLAG_ENERGY - set the threshold in energy (keV)

    print device.threshold(0, pixet.PX_THLFLAG_ENERGY) # gets the threshold of chip 0 in energy
    print device.threshold(pixet.MPXDACS_CHIP_ALL, pixet.PX_THLFLAG_ENERGY) # gets the threshold of all chip in energy

    device.setThreshold(0, 5, pixet.PX_THLFLAG_ENERGY)  # set threshold of chip 0, to 5 keV
    device.setThreshold(pixet.MPXDACS_CHIP_ALL, 5, pixet.PX_THLFLAG_ENERGY)  # set threshold of all chips to 5 keV
    device.setThreshold(pixet.MPXDACS_CHIP_ALL, 2, pixet.PX_THLFLAG_RELATIVE)  # increase threshold of all chips by 2

# -----------------------------------------------------------------------------------
#                         BIAS CONTROL
# -----------------------------------------------------------------------------------
def detExample4():
    device.setBias(100) # sets detector bias voltage to 100 V
    print device.bias() # return device bias volage (set value)
    print device.biasVoltageSense() # return sensed bias voltage
    print device.biasCurrentSense() # return sensed bias current

# -----------------------------------------------------------------------------------
#                         TIMEPIX CLOCK CONTROL
# -----------------------------------------------------------------------------------
def detExample5():
    print device.timepixClock()
    device.setTimepixClock(10) # sets timepix clock to 10 MHz


# -----------------------------------------------------------------------------------
#                      SENSOR REFRESH
# -----------------------------------------------------------------------------------
def detExample6():
    device.doSensorRefresh() # do the sensor refresh
    print device.isSensorRefreshSupported()
    device.enableSensorRefresh(True, 5) # enable sensor refresh, do the refresh each 5 seconds

# -----------------------------------------------------------------------------------
#                      PIXEL MATRIX CONFIGURATION
# -----------------------------------------------------------------------------------
def detExample7():
    pixcfg = device.pixCfg()
    pixcfg.maskAll(False) # unmask all matrix
    pixcfg.mask(10, True) # mask 10th pixel
    pixcfg.isMasked(10) # is 10th pixel masked ?
    pixcfg.maskRow(2, True) # mask second row
    pixcfg.maskColumn(2, True) # mask second column
    pixcfg.setModeAll(pixet.PX_TPXMODE_TOT) # sets whole matrix Timepix mode to TOT (PX_TPXMODE_MEDIPIX, PX_TPXMODE_TOT, PX_TPXMODE_TIMEPIX)

    mask = [1] * 65536
    mask[0] = 0 # mask first pixel
    pixcfg.setMaskMatrix(mask)

    thl = [7] * 65536
    pixcfg.setThlMatrix(thl) # set thl mask - all pixels to 7

    mode = [0] * 65536
    pixcfg.setModeMatrix(mode) # set tpx mode to medipix

    # get mask matrix
    chipByChip = False
    maskMatrix = pixcfg.maskMatrix(chipByChip)

# -----------------------------------------------------------------------------------
#                      READOUT PARAMETERS
# -----------------------------------------------------------------------------------
def detExample8():
    pars = device.parameters() # get parameters object
    par = pars.get("Temperature")  # temperature parameter in Minipix device
    temp = par.getDouble()
    print temp
