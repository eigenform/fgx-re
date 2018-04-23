#!/usr/bin/python

import os, sys
import hexdump
import struct

from fgx_format import *
from fgx_encode import *

if len(sys.argv) < 2:
    print("Usage: fgx-gci-info.py <filename>")
    exit(0)
else:
    filename = sys.argv[1]

# Import a GCI
input_gci = gci(filename)

# Decode the replay data
my_decoder = decoder(input_gci.get_replay_data())

# Get the decoded data
my_replay = my_decoder.dump()

# Manual transformations on our representation of the replay data go here ...
# -----------------------------------------------------------------------------

# Set the machine
#my_replay.player_array_dict[0]['char_id'] = 40

# Set the acceleration/speed slider (0x00 - 0x64 are "valid")
#my_replay.player_array_dict[0]['accel_speed_slider'] = 0x7F

# Play for 5,000 extra frames after the race finishes
#my_replay.total_frames = my_replay.total_frames + 5000

print("Total frames: {}".format(hex(my_replay.total_frames)))
print("Machine ID: {}".format(hex(my_replay.player_array_dict[0]['char_id'])))
print("Course ID: {}".format(hex(my_replay.course_id)))

# ...

# -----------------------------------------------------------------------------

# Re-encode the replay data
my_encoder = encoder()
new_replay_data = my_encoder.encode_gci(my_replay)

# Concatenate new replay data to the rest of the original GCI
input_gci.set_replay_data(new_replay_data)

# Recompute the checksum of the whole GCI
input_gci.recompute_checksum()

# Write the new GCI to a file
ofd = open("/tmp/fuzz.gci", "wb")
ofd.write(input_gci.raw_bytes)
ofd.close()
