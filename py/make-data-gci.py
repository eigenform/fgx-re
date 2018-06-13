#!/usr/bin/python

import os, sys
import hexdump
import struct
import binascii

from fgx_format import *
from fgx_encode import *


DATA_OFFSET = 0x240
DENTRY_SIZE = 0x40
BLOCK_SIZE = 0x2000
DOL_HEADER_SIZE = 0x100

if len(sys.argv) < 5:
    print("Usage: make-data-gci.py <input data filename> <blocksize> <GCI filename> <output .gci filename>")
    exit(0)
else:
    input_filename = sys.argv[1]
    num_blocks = int(sys.argv[2])
    dentry_filename = sys.argv[3]
    output_filename = sys.argv[4]

new_size = (num_blocks * BLOCK_SIZE) + DENTRY_SIZE

with open(input_filename, "rb") as f:
    data = f.read()
    input_data = bytearray(data)
    input_len = len(input_data)

if (input_len > (new_size - DENTRY_SIZE - DATA_OFFSET)):
    print("Your input file is too large to fit in {} blocks ({} bytes)".format(
          num_blocks, new_size))
    print("File length is {} bytes".format(input_len))
    exit(-1)

new_gci = gci(blocksize=num_blocks, gci_filename=dentry_filename)
new_gci.raw_bytes[DATA_OFFSET:(DATA_OFFSET+input_len)] = input_data

ofd = open(output_filename, "wb")
ofd.write(new_gci.raw_bytes)
ofd.close()
