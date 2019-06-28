#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Copyright (C) 2015 Daniel Turecek
#
# @file      pixet.py
# @author    Daniel Turecek <daniel@turecek.de>
# @date      2015-05-06
import pypixet
import code

pypixet.start()
pixet = pypixet.pixet
print(pixet.pixetVersion())

dev = pixet.devices()[0]
print("Found device: %s" % dev.fullName())

print("Doing acquisition...")
dev.doSimpleAcquisition(100, 0.1, pixet.PX_FTYPE_AUTODETECT, "./data.pmf")

# if you want to have interactive interpreter:
code.interact(local=locals())


