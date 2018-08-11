#!/usr/bin/python
''' make-data-gci.py
Synthesize a GCI file with arbitrary contents.
'''

import os, sys

from fgx_format import *
from fgx_encode import *

DENTRY_SIZE = 0x40
BLOCK_SIZE = 0x2000

if len(sys.argv) < 4:
    print("Usage: make-data-gci.py <input file> <dentry filename> <output file>")
    exit(0)
else:
    input_filename = sys.argv[1]
    dentry_filename = sys.argv[2]
    output_filename = sys.argv[3]

# Read input from some file 
with open(input_filename, "rb") as f:
    data = f.read()
    data_len = len(data)
    print("[*] Data is {} bytes".format(hex(data_len)))

# Round up size of data to the next block
aligned_len = (data_len & (~(BLOCK_SIZE-1))) + BLOCK_SIZE
print("[*] Padding to {} bytes".format(hex(aligned_len)))
padding_len = aligned_len - data_len
data += b'\x00' * padding_len
num_blocks = aligned_len // BLOCK_SIZE
print("[*] New GCI will be {} blocks".format(num_blocks))
print("[*] New GCI should be {} bytes".format(
    hex((BLOCK_SIZE*num_blocks)+DENTRY_SIZE)))

# Create a new dentry and add our data to it
new_gci = gci(blocksize=num_blocks, gci_filename=dentry_filename)
new_gci.raw_bytes += data

# Write to output file
with open(output_filename, "wb") as f:
    f.write(new_gci.raw_bytes)
    print("[*] Wrote {} bytes to {}".format(hex(len(new_gci.raw_bytes)),
        output_filename))
