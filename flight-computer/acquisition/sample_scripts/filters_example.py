import pydevcontrol

def getFirstMpxDev():
    # first get list of all connected Medipix devices
    devices = pixet.devicesByType(pixet.PX_DEVTYPE_MPX2)
    
    # get the first one
    dev = devices[0]
    return dev

def getDeviceFilter(dev, filterName):
    return pixet.filterMgr().deviceFilterByName(dev.asIDev(), filterName)



# get variables to device and filter:
dev = getFirstMpxDev()
filter = getDeviceFilter(dev, "Flat-Field")
# filter = getDeviceFilter(dev, "Beam-hardening")

# do some acquisition
acqCount = 1
acqTime = 0.5
fileName = ""
#fileName = "c:\\temp\\data.pmf"

rc = dev.doSimpleAcquisition(acqCount, acqTime, pixet.PX_FTYPE_AUTODETECT, fileName)
#rc = dev.doSimpleIntegralAcquisition(acqCount, acqTime, pixet.PX_FTYPE_AUTODETECT, fileName)
print "Acquition: %d" % rc

# get last frame
frame = dev.lastAcqFrameRefInc()

# get frame data to python array/list:
buff = pixet.RefI16Buff()
frame.data(buff, 0)
data = buff.data()
print data[0:10]


# filter frame
filtFrame = filter.filter(frame.asIData()).asIMpxFrame(0)

# get data
buff = pixet.RefI16Buff()
frame.data(buff, 0)
data = buff.data()
print data[0:10]

# save data to file
#frame.save("test.pmf", pixet.PX_FTYPE_AUTODETECT, 0)

# show filtered frame in main window:
di = pixet.plugin("devcontrol").privateInterface()
di.showFrame(dev.fullName(), frame)


# close frame !!
filtFrame.destroy()
# close frame !!
frame.destroy()
