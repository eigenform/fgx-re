#!/usr/bin/python

"""
Example using fgx_{encode,format}.py to decode a replay file.
The decoded representation of replay data lives in the my_replay object.
"""

import os, sys
import hexdump
import struct
import binascii

from fgx_format import *
from fgx_encode import *

if len(sys.argv) < 2:
    print("Usage: fgx-replay-info.py <filename>")
    exit(0)
else:
    filename = sys.argv[1]

# Import a GCI
input_gci = gci(filename)
print("Read GCI: {}".format(input_gci.get_filename()))


# Decode the replay data
my_decoder = decoder(input_gci.get_replay_data())

# Get the decoded data
my_replay = my_decoder.dump()

# Write replay data out to a binary file

print("----------------------------------------------------------------------")
print("Replay array entries: {}".format(hex(my_replay.replay_array_entries)))
print("Total frames: {}".format(hex(my_replay.total_frames)))

num_frames = 0
current_frame = 0
output = bytearray()
for entry in my_replay.replay_array_dict:
    mask      = entry['mask']
    strafe    = entry['strafe']
    accel     = entry['accel']
    brake     = entry['brake']
    frames    = entry['frames'] + 1
    steer_x   = entry['steer_x']
    steer_y   = entry['steer_y']

    # Get a total frame count by adding up all entries
    num_frames += frames

    # Build binary replay_array output
    output += struct.pack("@7B", mask, strafe, accel, brake, frames-1, steer_x, steer_y)

    # Unroll each entry
    for frame in range(0,frames):
        print("frame={:05d}: accel={:02X}, mask={:02X}, steer_x=0x{:02X}, steer_y=0x{:02X}".format(current_frame, accel,
            mask, steer_x, steer_y))
        current_frame += 1

print("Calculated total number of frames from entries: {}".format(num_frames))
print("Size of binary output: {} ({})".format(hex(len(output)), len(output)))
with open("/tmp/replay.bin", "wb") as f:
    f.write(output)


print("----------------------------------------------------------------------")
