#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# DPD Calculation Engine main file.
#
# http://www.opendigitalradio.org
# Licence: The MIT License, see notice at the end of this file

"""This Python script is the main file for ODR-DabMod's DPD Computation Engine.
This engine calculates and updates the parameter of the digital
predistortion module of ODR-DabMod."""

import logging
logging.basicConfig(format='%(asctime)s - %(module)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='/tmp/dpd.log',
                    filemode='w',
                    level=logging.DEBUG)

import src.Measure as Measure
import src.Model as Model
import src.Adapt as Adapt
import argparse

parser = argparse.ArgumentParser(description="DPD Computation Engine for ODR-DabMod")
parser.add_argument('--port', default='50055',
        help='port of DPD server to connect to (default: 50055)',
        required=False)
parser.add_argument('--rc-port', default='9400',
        help='port of ODR-DabMod ZMQ Remote Control to connect to (default: 9400)',
        required=False)
parser.add_argument('--samplerate', default='8192000',
        help='Sample rate',
        required=False)
parser.add_argument('--coefs', default='dpdpoly.coef',
        help='File with DPD coefficients, which will be read by ODR-DabMod',
        required=False)
parser.add_argument('--samps', default='10240',
        help='Number of samples to request from ODR-DabMod',
        required=False)

cli_args = parser.parse_args()

port = int(cli_args.port)
port_rc = int(cli_args.rc_port)
coef_path = cli_args.coefs
num_req = int(cli_args.samps)
samplerate = int(cli_args.samplerate)

meas = Measure.Measure(samplerate, port, num_req)
adapt = Adapt.Adapt(port_rc, coef_path)
coefs = adapt.get_coefs()
model = Model.Model(coefs)

for i in range(10):
    txframe_aligned, _, rxframe_aligned, _ = meas.get_samples()
    coefs = model.get_next_coefs(txframe_aligned, rxframe_aligned)
    adapt.set_coefs(coefs)

# The MIT License (MIT)
#
# Copyright (c) 2017 Andreas Steger, Matthias P. Braendli
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
