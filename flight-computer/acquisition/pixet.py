#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Copyright (C) 2015 Daniel Turecek
#
# @file      pixet.py
# @author    Daniel Turecek <daniel@turecek.de>
# @date      2015-05-06
import pypixet
import time

pypixet.start()
pixet = pypixet.pixet
print(pixet.pixetVersion())

dev = pixet.devices()[0]
print("Found device: %s" % dev.fullName())

print("Doing acquisition...")
startTime = time.time()
dev.doSimpleAcquisition(10, 0.1, pixet.PX_FTYPE_AUTODETECT, "./data.pmf")
print("Finished in %d seconds" % (time.time() - startTime))

