#!/usr/bin/python

import os, sys
import hexdump
from fgx_compression import *

def log(msg): print("[*] {}".format(msg))
def err(msg): print("[!] {}".format(msg))

# -----------------------------------------------------------------------------
# Define some known values for known fields in the GCI

class region:
    """ Game ID bytes, corresponds to game region.
        (4 bytes @ offset 0x00)
    """
    pal =   b'GFZP'
    jp =    b'GFZJ'
    ntsc =  b'GFZE'
    string = {  pal: "PAL", jp: "JP", ntsc: "NTSC", }

    def get_region(x):
        """ Given some raw game ID bytes, return the corresponding string """
        if x in region.string:
            return "{} ({})".format(region.string.get(x), x.hex())
        else:
            return "Unknown ({})".format(x)

class ft:
    """ Known filetype bytes.
        (2 bytes @ offset 0x42)
    """
    replay =    b'\x05\x04'
    game =      b'\x01\x0b'
    ghost =     b'\x02\x01'
    garage =    b'\x03\x01'
    emblem =    b'\x04\x01'

    string = {  replay: "Replay file",
                game: "Gamedata file",
                garage: "Garage file",
                ghost: "Ghost file",
                emblem: "Emblem file", }

    def get_filetype(x):
        """ Given some raw filetype bytes, return the corresponding string """
        if x in ft.string:
            return "{} ({})".format(ft.string.get(x), x.hex())
        else:
            return "Unknown ({})".format(x.hex())





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
    test = decompressor(replay_data)
    test._decompress_header()
    test._decompress_array()

    # Write output as a hexdump
    #log("Header section:")
    #hexdump.hexdump(test.output)

    log("Replay array")
    hexdump.hexdump(test.replay_array)
