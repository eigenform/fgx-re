#!/usr/bin/python

import os, sys
import hexdump
import struct

from fgx_format import *
from fgx_encode import *

def log(msg): print("[*] {}".format(msg))
def err(msg): print("[!] {}".format(msg))




# -----------------------------------------------------------------------------
# Initialize some variables here.
#   * Shuffle relevant data from the dentry into the raw[] dict as bytes.
#   * Use info[] to store information relevant to the user.

raw = {}
info = {}


# -----------------------------------------------------------------------------
# Handle arguments here

if len(sys.argv) < 2:
    print("Usage: fgx-gci-info.py <filename>")
    exit(0)
else:
    filename = sys.argv[1]


# -----------------------------------------------------------------------------
# Try to open() the file provided by the user; otherwise, die
try:
    f = open(filename, "rb")
    log("Read {} bytes from {}".format(hex(os.stat(filename).st_size), filename))
except FileNotFoundError as e:
    err(e)
    exit(-1)

outfile_base = os.path.basename(filename).split(".")[0]

# -----------------------------------------------------------------------------
# Read some relevant fields from the GCI

dentry = f.read(0x40)
raw['game_id'] = dentry[0:4]
raw['checksum'] = f.read(2)
raw['ft'] = f.read(2)

info['checksum'] = raw['checksum'].hex()
info['ft'] = ft.get_filetype(raw['ft'])
info['region'] = region.get_region(raw['game_id'])


# -----------------------------------------------------------------------------
# Write some information about the provided GCI file to stdout. If we end up
# writing 'None' to stdout, this probably indicates that we're trying to
# handle some invalid or unknown value for some field.

#log("Checksum: {}".format(info['checksum']))
#log("Filetype: {}".format(info['ft']))
#log("Region: {}".format(info['region']))
#log("Dentry looks like this:")
#hexdump.hexdump(dentry)
#print()



# -----------------------------------------------------------------------------
# Read uncompressed data from replay files
if raw['ft'] == ft.replay:
    f.seek(0x20a0)
    replay_data = bytearray(f.read())
    test = decoder(replay_data)
    test._decode_header()
    test._decode_array()

    headerfile = open(outfile_base + ".header.bin", "wb")
    headerfile.write(test.header)
    headerfile.close()
    arrayfile = open(outfile_base + ".array.bin", "wb")
    arrayfile.write(test.replay_array)
    arrayfile.close()

    

    #co = encoder(test.header)

    #r28_unk0, r28_unk1, r28_unk2, r28_unk3, r28_unk4, r24_loop1, = (0,)*6
    #unk_entries, r18_loop2, r25_loop3, r23_unk1 = (0,)*4
    #r20_unk1 = 5

    #co._encode(8, co.header[co.offset], header=True)
    #co._encode(7, co.header[co.offset], header=True)
    #co._encode(6, co.header[co.offset], header=True)
    #co._encode(32, co.header[co.offset], header=True)
    #co._encode(32, co.header[co.offset], header=True)

    #unk_entries = co.header[co.offset]
    #co._encode(5, co.header[co.offset], header=True)

    #co._encode(3, co.header[co.offset], header=True)
    #co._encode(2, co.header[co.offset], header=True)
    #co._encode(1, co.header[co.offset], header=True)
    #co._encode(7, co.header[co.offset], header=True)
















    #hexdump.hexdump(co.output)
