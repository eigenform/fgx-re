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

print("----------------------------------------------------------------------")
print("Number of replay array entries: {}".format(my_replay.replay_array_entries))
for entry in my_replay.replay_array_dict:
    print(entry)

print("----------------------------------------------------------------------")

print("Total frames: {}".format(hex(my_replay.total_frames)))
print("Machine ID: {}".format(hex(my_replay.player_array_dict[0]['char_id'])))
print("Course ID: {}".format(hex(my_replay.course_id)))
print("Replay array entries: {}".format(hex(my_replay.replay_array_entries)))
print("unk_array entries: {}".format(hex(my_replay.unk_array_entries)))
print("player_array entries: {}".format(hex(my_replay.player_array_entries)))
