#!/usr/bin/python

import os, sys
import hexdump
import struct
import binascii

from fgx_format import *
from fgx_encode import *

BLOCKSIZE = 3
NEW_SIZE = (BLOCKSIZE * 0x2000) + 0x40

if len(sys.argv) < 4:
    print("Usage: make-data-gci.py <input data filename> <GCI filename> <output .gci filename>")
    exit(0)
else:
    input_filename = sys.argv[1]
    dentry_filename = sys.argv[2]
    output_filename = sys.argv[3]

with open(input_filename) as f:
    input_data = bytearray(f.read(), 'ascii')
    input_len = len(input_data)

if (input_len > (NEW_SIZE - 0x40 - 0x100)):
    print("Your input file is too large to fit in {} blocks ({} bytes)".format(
          BLOCKSIZE, input_len))
    exit(-1)

new_gci = gci(blocksize=BLOCKSIZE, gci_filename=dentry_filename)
new_gci.raw_bytes[0x100:(0x100+input_len)] = input_data

ofd = open(output_filename, "wb")
ofd.write(new_gci.raw_bytes)
ofd.close()
