import struct

class decoder(object):
    def __init__(self, encoded_data):

        # Internal state
        self.input = encoded_data       # bytearray of encoded GCI data 
        self.total_iter = 0             # total number of `_decode()` iters

        self.output = bytearray()       # all output data (32-bit numbers)
        self.header = bytearray()       # header data (32-bit numbers)

        
        
        # Decoded data fields are below (decoded from top-to-bottom)
        self.tick = 0                   # timestamp associated with this file
        self.player_entry_size = 0      # (controls iteration over player_array)
        self.unk_1 = 0
        self.unk_2 = 0
        self.player_array_entries = 0   # 1 in time-attack, 0x1e in grand-prix
        self.unk_3 = 0
        self.unk_4 = 0
        self.unk_5 = 0
        self.unk_6 = 0

        self.player_array_dict = []
        self.player_array = bytearray()

        self.unk_one_bit_array = []     # Array of one-bit decodings (one per player_entry)
        self.unk_two_bit_array = []     # Array of two-bit decodings (one per player_entry)
        self.total_frames = 0           # Length of replay in frames (??)

        self.unk_array_entries = 0      # 4 in time-attack replays
        self.unk_array = []             # Unknown array, 4 entries in time-attack replays

        self.replay_array_entries = 0   # number of entries in replay_array
        self.replay_array = bytearray() # replay_array structure
        self.replay_array_dict = []


    def _decode(self, count, signed=False, header=False):
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

        # Preserve an array with the full 32-bit output of each call.
        self.output += result.to_bytes(4, byteorder='big', signed=signed)
        if (header is True):
            self.header += result.to_bytes(4, byteorder='big', signed=signed)
        #print("iter={:08X}: {:08X}".format(self.total_iter, result))
        return result

    def _decode_header(self):
        unk_entry_idx = 0

        unk_entries = 0
        unk_byte = 0

        self.tick = self._decode(8, header=True) 
        self.player_entry_size = self._decode(7, header=True)
        self._decode(6, header=True) # arg to calls at end of this func
        self.unk_1 = self._decode(32, header=True) #word stored at 803f3a00
        self.unk_2 = self._decode(32, header=True) #word stored at 801a63c0
        self.player_array_entries = self._decode(5, header=True)
        self.unk_3 = self._decode(3, header=True) #half-word stored at 803ffd88
        self.unk_4 = self._decode(2, header=True) # not saved by decompression
        self.unk_5 = self._decode(1, header=True) # determines calls at end of this func
        self.unk_6 = self._decode(7, header=True) # arg to calls at end of this func

        # I think each entry decoded here represents each player in a replay.
        while (unk_entry_idx < self.player_array_entries):

            #self.replay_array += steer_y.to_bytes(1, byteorder='big')
            entry = {}
            entry_ba = bytearray()

            is_human = self._decode(1, header=True) #human=0x01, cpu=0x00
            char_id = self._decode(6, header=True) #falcon=0x6, dr.stew=0x2, pico=0x5, etc

            if (self.player_entry_size > 3): 
                member_0x4 = self._decode(5, header=True)

            if (self.player_entry_size > 2):
                accel_speed_slider = self._decode(7, header=True) #0x00=max_accel, 0x64=max_speed

            if (is_human != 0):
                member_0x2 = self._decode(2, header=True)

                if (self.player_entry_size < 2): # for non-replay data (?)
                    accel_speed_slider = self._decode(7, header=True)

                # Don't know if this is for garage ships or not yet
                is_custom_ship = self._decode(1, header=True)
                if ((is_custom_ship & 0x000000FF) != 0):
                    for i in range(0, 33216):
                        self._decode(8, header=True)
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

            #entry_ba += is_human.to_bytes(1, byteorder='big')
            #entry_ba += char_id.to_bytes(1, byteorder='big')
            #entry_ba += member_0x2.to_bytes(1, byteorder='big')
            #entry_ba += accel_speed_slider.to_bytes(1, byteorder='big')
            #entry_ba += member_0x4.to_bytes(1, byteorder='big')
            #entry_ba += is_custom_ship.to_bytes(1, byteorder='big')

            self.player_array_dict.append(entry)

        # Two arrays here, one entry for each player_array entry
        if (self.player_entry_size > 4):
            for i in range(0, unk_entry_idx):
                self.unk_one_bit_array.append(self._decode(1, header=True))
        for i in range(0, unk_entry_idx):
            self.unk_two_bit_array.append(self._decode(2, header=True))

        # I don't actually know for certain if this is the number of frames, 
        # but it sure feels like it.
        if (self.player_entry_size >= 5):
            self.total_frames = self._decode(20, header=True)

    def _decode_array(self):
        r21_loop2, r19_loop3 = (0,)*2
        self.unk_array_entries = self._decode(8, header=True)

        for i in range(0, self.unk_array_entries):
            entry = []
            entry.append(self._decode(14, header=True))
            entry.append(self._decode(14, header=True))
            entry.append(self._decode(4, header=True))
            entry.append(self._decode(5, header=True))
            entry.append(self._decode(5, header=True))
            entry.append(self._decode(5, header=True))
            entry.append(self._decode(5, header=True))
            entry.append(self._decode(5, header=True))

            # I think for time-attack its safe to assume this only runs once? 
            r19_loop3 = 0
            r21_loop2 = 1
            while (r19_loop3 < r21_loop2):
                entry.append(self._decode(32, header=True))
                entry.append(self._decode(32, header=True))
                entry.append(self._decode(32, header=True))
                entry.append(self._decode(32, header=True))
                entry.append(self._decode(32, header=True))
                entry.append(self._decode(32, header=True))
                r19_loop3 += 1

            entry.append(self._decode(32, header=True))
            entry.append(self._decode(32, header=True))
            entry.append(self._decode(32, header=True))
            entry.append(self._decode(32, header=True))
            entry.append(self._decode(32, header=True))
            entry.append(self._decode(32, header=True))
            self.unk_array.append(entry)

        self.replay_array_entries = self._decode(14, header=True)

        for idx in range(0, self.replay_array_entries + 1):
            entry = {}
            mask =      self._decode(8)
            strafe =    self._decode(8)
            accel =     self._decode(7)
            brake =     self._decode(7)
            frames =    self._decode(8)
            steer_x =   self._decode(8)
            steer_y =   self._decode(8)

            self.replay_array += mask.to_bytes(1, byteorder='big')
            self.replay_array += steer_x.to_bytes(1, byteorder='big')
            self.replay_array += steer_y.to_bytes(1, byteorder='big')
            self.replay_array += strafe.to_bytes(1, byteorder='big')
            self.replay_array += accel.to_bytes(1, byteorder='big')
            self.replay_array += brake.to_bytes(1, byteorder='big')
            self.replay_array += frames.to_bytes(1, byteorder='big')

            entry['mask'] = mask
            entry['strafe'] = strafe
            entry['accel'] = accel
            entry['brake'] = brake
            entry['frames'] = frames
            entry['steer_x'] = steer_x
            entry['steer_y'] = steer_y
            self.replay_array_dict.append(entry)

class encoder(object):
    """
    The constructor needs references to all objects to-be-packed into the
    GCI. For now, we split this up into:

        * Some bytearray for header data. These are not arranged contiguously
          in memory, so we're just storing them as an array of 32 bit numbers,
          one for each call to `_decode()`.

        * Some bytearray for the array of replay entry structures

    in-memory header structures encoded and stored in GCI:
        0x10(sp) ;u32
        0x14(sp) ;u8
        0x15(sp) ;u8
        0x19(sp) ;u8

        0x08(r4) ;u16

        0x0(r23) ;u8
        0x1(r23) ;u8
        0x2(r23) ;u8
        0x3(r23) ;u8
        0x4(r23) ;u8

        0x3c(r25) ;u8

        0x38(r26) ;u8

        0x08(r5) ;u32

        -0x0110(r6) ;u16

        0xff4c(array_base) ;u16
        0xff50(array_base) ;u16
        
        0xff4c(array_base) ;u32 (yes, same data as above)
        0xff4e(array_base) ;u8

        0xff50(array_base) ;u32
         


    """

    def __init__(self, input_header):

        # A bytearray of 8-bit numbers (one for each call to `_encode()`).
        # Maximum output size is 0x8c000 (?)
        self.output = bytearray([0]*1000)

        # Store the raw header as an array of 32-bit numbers
        # (this is probably convoluted)
        offset = 0
        self.header = []
        while (offset < len(input_header) ):
            x = struct.unpack(">L", input_header[offset:offset+4])[0]
            self.header.append(x)
            offset += 4
        self.offset = 0

        # The total number of iterations we've taken in `_decode()`
        self.total_iter = 0

    def _encode(self, count, val, header=False, replay=False):
        result = 0
        #self.output += result.to_bytes(4, byteorder='big')
        num_iter = count
        if (num_iter == 0): return None
        while (count > 0):
            base_offset = (self.total_iter >> 3) & 0x1fffffff
            #print("output_target={}".format(hex(self.output[base_offset])))
            if (base_offset < 0x8c000):
                mask = self.total_iter & 0x00000007
                if ( val & ( 1 << (num_iter - 1) ) != 0 ):
                        self.output[base_offset] = self.output[base_offset] | (1 << mask)
                self.total_iter += 1
                num_iter = num_iter - 1
                count = count - 1

        self.offset += 1
        return self.output[base_offset]
