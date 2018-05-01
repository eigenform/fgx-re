import struct
import hexdump

class replay(object):
    """
    Representation of some replay. These fields correspond to pieces of
    information that are filled out by the decoder.
    """

    def __init__(self):
        # 8 bits.
        # Every time a replay is saved, the first byte encoded is
        # the lower 8 bits from a timestamp (a call to OsGetTick()).
        self.tick = 0

        # 7 bits.
        # This controls the parsing of the "player_array" structure.
        # This is always 0x5 for replays (??).
        self.player_entry_size = 0

        # 6 bits.
        # Course/track ID? Arg to calls at end of decoding func.
        self.course_id = 0

        # 32 bits.
        # Unknown. word stored at 803f3a00
        self.unk_1 = 0

        # 32 bits.
        # Unknown. word stored at 801a63c0
        self.unk_2 = 0

        # 5 bits.
        # The number of members in the "player_array" structure.
        # Always 1 in time-attack replays, always 0x1e in grand-prix replays.
        self.player_array_entries = 0

        # 3 bits.
        # Unknown. half-word at 803ddf88
        self.unk_3 = 0

        # 2 bits.
        # Unknown. not saved by decoding function (??)
        self.unk_4 = 0

        # 1 bit.
        # Unknown. arg to calls at end of decoding func
        self.unk_5 = 0

        # 7 bits.
        # Unknown. arg to calls at end of decoding func
        self.unk_6 = 0

        # An array of size 'player_array_entries'.
        self.player_array_dict = []

        # An array of garage-data entries where each entry corresponds to a play_array entry
        self.garage_data = []

        # Unknown array of one-bit decodings (one per player_entry)
        self.unk_one_bit_array = []

        # Unknwon array of two-bit decodings (one per player_entry)
        self.unk_two_bit_array = []

        # 20 bits.
        # Length of replay in frames (??)
        self.total_frames = 0

        # 8 bits.
        # Number of entries in the following array.
        # Always 4 in time-attack replays?
        self.unk_array_entries = 0

        # Unknown array.
        self.unk_array = []

        # 14 bits.
        # Number of entries in replay_array
        self.replay_array_entries = 0

        # replay_array structure
        self.replay_array_dict = []


class decoder(object):
    def __init__(self, input_data):

        # Internal state
        self.raw_output = bytearray()
        self.input = input_data

        # We have to keep track of the number of iterations taken by `_decode()`
        self.total_iter = 0

        # After loading some input data, decode it and fill out `self.replay`
        self.replay = replay()
        self._decode_header()
        self._decode_array()

    def dump(self):
        return self.replay

    def _decode(self, count, signed=False):
        #print("count={} offset=0x{:08X}, input=0x{:08X}, total_iter=0x{:08X}".format(count, (self.total_iter >> 3)&0x1fffffff, self.input[(self.total_iter >> 3)&0x1fffffff], self.total_iter))
        result = 0
        num_iter = count
        if count < 1: return None
        while(count != 0):
            base_offset = (self.total_iter >> 3) & 0x1fffffff
            input_val = self.input[base_offset]
            mask = self.total_iter & 0x00000007
            mask = 1 << (mask & 0x1F)
            if (mask & input_val):
               result = result | (1 << ((num_iter - 1) & 0x1F))
            num_iter = num_iter - 1
            count = count - 1
            self.total_iter += 1

        # Save full 32-bit output from all calls to decode (for debugging)
        #print(hex(result))
        #print("output: {:08X}".format(result))
        self.raw_output += result.to_bytes(4, byteorder='big', signed=signed)

        return result

    def _decode_header(self):
        unk_entry_idx = 0
        unk_entries = 0
        unk_byte = 0

        self.replay.tick = self._decode(8)
        self.replay.player_entry_size = self._decode(7)
        self.replay.course_id = self._decode(6) # arg to calls at end of this func
        self.replay.unk_1 = self._decode(32) #word stored at 803f3a00
        self.replay.unk_2 = self._decode(32) #word stored at 801a63c0
        self.replay.player_array_entries = self._decode(5)
        self.replay.unk_3 = self._decode(3) #half-word stored at 803ffd88
        self.replay.unk_4 = self._decode(2) # not saved by decompression
        self.replay.unk_5 = self._decode(1) # determines calls at end of this func
        self.replay.unk_6 = self._decode(7) # arg to calls at end of this func

        # I think each entry decoded here represents each player in a replay.
        while (unk_entry_idx < self.replay.player_array_entries):
            entry = {}
            entry_ba = {}

            is_human = self._decode(1) #human=0x01, CPU=0x00
            char_id = self._decode(6)

            if (self.replay.player_entry_size > 3):
                member_0x4 = self._decode(5)

            if (self.replay.player_entry_size > 2):
                accel_speed_slider = self._decode(7)

            if (is_human != 0):
                member_0x2 = self._decode(2)

                if (self.replay.player_entry_size < 2): # for non-replay data (?)
                    accel_speed_slider = self._decode(7)

                # Don't know if this is for garage ships or not yet
                is_custom_ship = self._decode(1)
                if ((is_custom_ship & 0x000000FF) != 0):
                    custom_ship_data = bytearray()
                    print("garage data decode")
                    for i in range(0, 33216):
                        word = self._decode(8)
                        custom_ship_data += word.to_bytes(1, byteorder='big')
                else:
                    custom_ship_data = None
                unk_entry_idx += 1

            elif (is_human == 0):
                member_0x2 = 0
                accel_speed_slider = 0
                unk_entry_idx += 1

            entry['is_human'] = is_human
            entry['char_id'] = char_id
            entry['member_0x2'] = member_0x2
            entry['accel_speed_slider'] = accel_speed_slider
            entry['member_0x4'] = member_0x4
            entry['is_custom_ship'] = is_custom_ship
            entry['custom_ship_data'] = custom_ship_data
            self.replay.player_array_dict.append(entry)

        # Two arrays here, one entry for each player_array entry
        if (self.replay.player_entry_size > 4):
            for i in range(0, unk_entry_idx):
                entry = self._decode(1)
                self.replay.unk_one_bit_array.append(entry)
        for i in range(0, unk_entry_idx):
            entry = self._decode(2)
            self.replay.unk_two_bit_array.append(entry)

        if (self.replay.player_entry_size >= 5):
            self.replay.total_frames = self._decode(20)

    def _decode_array(self):
        r21_loop2, r19_loop3 = (0,)*2
        self.replay.unk_array_entries = self._decode(8)

        for i in range(0, self.replay.unk_array_entries):
            entry = {}
            part_one = []
            part_one.append(self._decode(14))
            part_one.append(self._decode(14))
            part_one.append(self._decode(4))
            part_one.append(self._decode(5))
            part_one.append(self._decode(5))
            part_one.append(self._decode(5))
            part_one.append(self._decode(5))
            part_one.append(self._decode(5))
            entry['part_one'] = part_one

            # I think for time-attack its safe to assume this only runs once?
            r19_loop3 = 0
            r21_loop2 = 1
            part_two = []
            while (r19_loop3 < r21_loop2):
                part_two.append(self._decode(32))
                part_two.append(self._decode(32))
                part_two.append(self._decode(32))
                part_two.append(self._decode(32))
                part_two.append(self._decode(32))
                part_two.append(self._decode(32))
                r19_loop3 += 1
            entry['part_two'] = part_two

            part_three = []
            part_three.append(self._decode(32))
            part_three.append(self._decode(32))
            part_three.append(self._decode(32))
            part_three.append(self._decode(32))
            part_three.append(self._decode(32))
            part_three.append(self._decode(32))
            entry['part_three'] = part_three

            self.replay.unk_array.append(entry)

        self.replay.replay_array_entries = self._decode(14)
        for idx in range(0, self.replay.replay_array_entries + 1):
            entry = {}
            mask =      self._decode(8)
            strafe =    self._decode(8)
            accel =     self._decode(7)
            brake =     self._decode(7)
            frames =    self._decode(8)
            steer_x =   self._decode(8)
            steer_y =   self._decode(8)

            entry['mask'] = mask
            entry['strafe'] = strafe
            entry['accel'] = accel
            entry['brake'] = brake
            entry['frames'] = frames
            entry['steer_x'] = steer_x
            entry['steer_y'] = steer_y
            self.replay.replay_array_dict.append(entry)

class encoder(object):
    def __init__(self):

        # This is the output generated by calling `encode_gci()`
        self.output = bytearray([0]*0x8c000)

        # `_encode()` must maintain an offset/cursor into the output buffer
        self.offset = 0

        # The total number of iterations we've taken in `_encode()` calls
        self.total_iter = 0
        self.bytes_written = 0

    def _encode(self, count, val):
        result = 0
        num_iter = count
        if (num_iter == 0): return None
        while (count > 0):
            base_offset = (self.total_iter >> 3) & 0x1fffffff
            if (base_offset < 0x8c000):
                mask = self.total_iter & 0x00000007
                if ( val & ( 1 << (num_iter - 1) ) != 0 ):
                        self.output[base_offset] = self.output[base_offset] | (1 << mask)
                self.total_iter += 1
                num_iter = num_iter - 1
                count = count - 1
        self.offset += 1
        self.bytes_written += 1
        return self.output[base_offset]


    def encode_gci(self, data):
        """
        Expects a `class replay` filled out by the decoder,
        (or imported from a file, maybe sometime down the road)
        """
        self._encode(8, data.tick)

        # Note that the following loops do not conditionally encode bits 
        # based on the value of player_entry_size.

        self._encode(7, data.player_entry_size)
        self._encode(6, data.course_id)
        self._encode(32, data.unk_1)
        self._encode(32, data.unk_2)
        self._encode(5, data.player_array_entries)
        self._encode(3, data.unk_3)
        self._encode(2, data.unk_4)
        self._encode(1, data.unk_5)
        self._encode(7, data.unk_6)

        # Note that the array size is decoupled from player_array_size here
        for entry in data.player_array_dict:
            self._encode(1, entry['is_human'])
            self._encode(6, entry['char_id'])
            self._encode(5, entry['member_0x4'])
            self._encode(7, entry['accel_speed_slider'])
            self._encode(2, entry['member_0x2'])
            self._encode(1, entry['is_custom_ship'])
            if (entry['is_custom_ship'] == 1):
                for i in range(0, 33216):
                    self._encode(8, entry['custom_ship_data'][i])

        for entry in data.unk_one_bit_array:
            self._encode(1, entry)
        for entry in data.unk_two_bit_array:
            self._encode(2, entry)

        self._encode(20, data.total_frames)

        self._encode(8, data.unk_array_entries)
        # Note that the array size is decoupled from unk_array_entries here
        for entry in data.unk_array:
            self._encode(14, entry['part_one'][0])
            self._encode(14, entry['part_one'][1])
            self._encode(4, entry['part_one'][2])
            self._encode(5, entry['part_one'][3])
            self._encode(5, entry['part_one'][4])
            self._encode(5, entry['part_one'][5])
            self._encode(5, entry['part_one'][6])
            self._encode(5, entry['part_one'][7])
            for word in entry['part_two']:
                self._encode(32, word)
            for word in entry['part_three']:
                self._encode(32, word)

        self._encode(14, data.replay_array_entries)
        # Note that the array size is decoupled from replay_array_entries here
        for entry in data.replay_array_dict:
            self._encode(8, entry['mask'])
            self._encode(8, entry['strafe'])
            self._encode(7, entry['accel'])
            self._encode(7, entry['brake'])
            self._encode(8, entry['frames'])
            self._encode(8, entry['steer_x'])
            self._encode(8, entry['steer_y'])

        print("Wrote {} bytes of encoded output".format(hex(self.bytes_written)))
        return self.output
