#!/usr/bin/python

"""
Example for manually playing with fields in replay data
"""

import os, sys
import hexdump
import struct
import binascii

from fgx_format import *
from fgx_encode import *

if len(sys.argv) < 3:
    print("Usage: replay-fuzz.py <filename> <output filename>")
    exit(0)
else:
    filename = sys.argv[1]
    output_filename = sys.argv[2]

# Import a GCI
input_gci = gci(filename)
print(input_gci.get_filename())


# -----------------------------------------------------------------------------
# Filename fuzzing

#random_fn = bytearray(b'fzr0000' +(os.urandom(18)) + b".dat\x00\x00\x00")
#random_fn = bytearray(b'fzr0000' +(os.urandom(18)) + b".dat\x00\x00\x00")
#random_fn = bytearray(b'fzr0000' + os.urandom(1) + b"F8052EE2A0E6C64A0.dat\x00\x00\x00")
#random_fn = bytearray(b'fzr0000' + b'\xbc' + b"F8052EE2A0E6C64A0.dat\x00\x00\x00")
#random_fn = bytearray(b'fzr0000' + b"3F8052EE2A0E6C64A0.dat\x00\x00\x00")
#random_fn = bytearray(b'f_zero_debug.dat' + b'\x00'*16)
#input_gci.set_filename(random_fn)
#print(input_gci.get_filename())

# -----------------------------------------------------------------------------
# Fuzz replay data after the player_array with random bytes

# Oh god this dies in strcpy() for 8-block replays with garage data (??)
#input_gci.raw_bytes[0x20b0:] = bytearray(b'Z'*0xdf90)

#input_gci.raw_bytes[0x20b0:] = bytearray(os.urandom(0xdf90))
#input_gci.raw_bytes[0x20b0:] = bytearray(b'\x00'*0xdf90)


# Decode the replay data
my_decoder = decoder(input_gci.get_replay_data())

# Get the decoded data
my_replay = my_decoder.dump()

# -----------------------------------------------------------------------------
# Fuzzing the decoded representation of the replay data

# Test fields associated with the first player_array entry

#my_replay.player_array_dict[0]['char_id'] = 40
#my_replay.player_array_dict[0]['accel_speed_slider'] = 0x7F

# Play for 5,000 extra frames after the race finishes
#my_replay.total_frames = my_replay.total_frames + 5000

# If you give an invalid course ID, we always die on invalid reads.
# Probably need to test this more extensively?


# -----------------------------------------------------------------------------
# Re-encode the replay data
my_encoder = encoder()
new_encoded_replay_data = my_encoder.encode_gci(my_replay)

# Concatenate new replay data to the rest of the original GCI
#input_gci.set_replay_data(new_encoded_replay_data)

# Recompute the checksum of the whole GCI
# Force region to NTSC
input_gci.recompute_checksum()
input_gci.set_region(region.ntsc)

# Write the new GCI to a file
print("Writing to {}".format(output_filename))
ofd = open(output_filename, "wb")
ofd.write(input_gci.raw_bytes)
ofd.close()
