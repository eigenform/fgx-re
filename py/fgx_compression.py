import struct

class decompressor(object):
    """
    This object has to keep track of four things:

        * The total number of bits (?) we've decoded from the GCI
        * The input data buffer (compressed data from the GCI itself)

        * All output data (all 32 bits from all results) for reference.
          Note that this bytearray only accurately represents the order in
          which we decompressed bytes, and does not represent the way that
          decompressed bytes are organized in-memory

        * The "header" bytes (or basically, bytes that aren't array bytes).
          It's not clear what they are, yet.

        * The replay array - where each entry looks like this in-memory:

                struct replay_entry {
                    uint8_t mask;
                    int8_t steer_x;
                    int8_t steer_y;
                    int8_t strafe;
                    uint8_t accel;
                    uint8_t brake;
                    uint8_t frames;
                };

          Note that the layout of data in the replay array is independent of
          the order in which bytes are decoded. The actual order for decoding
          an entry should look like this:

                    mask =      self._decompress(8)
                    strafe =    self._decompress(8)
                    accel =     self._decompress(7)
                    brake =     self._decompress(7)
                    frames =    self._decompress(8)
                    steer_x =   self._decompress(8)
                    steer_y =   self._decompress(8)
    """

    def __init__(self, compressed_data ):

        # A bytearray with the compressed data from the GCI
        self.input = compressed_data

        # A bytearray of 32-bit numbers (one for each call to `_decompress()`)
        self.output = bytearray()

        # The header data, currently just a bytearray of 32-bit numbers
        self.header = bytearray()

        # The decompressed replay array structure
        self.replay_array = bytearray()
        self.replay_entries = 0

        # The total number of iterations we've taken in `_decompress()`
        self.total_iter = 0

    def _decompress(self, count, signed=False, header=False):
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

        # In one sense, we want to keep the 32-bit output around because
        # the compression function operates on a whole 32-bit register
        # (so at least if we're going to define a format for storing the
        # raw data *outside of the game* we might as well keep all the
        # bits around until we understand the functions accepting input).

        self.output += result.to_bytes(4, byteorder='big', signed=signed)

        if (header is True):
            self.header += result.to_bytes(4, byteorder='big', signed=signed)

        # But in another sense, the actual bits of the result used by other
        # functions seems to vary; the high-level decompression functions
        # usually mask away bits before writing them somewhere in memory
        # during decompression.
        #
        #self.output += result.to_bytes(((result.bit_length() + 7) // 8), byteorder='big')

        #print("iter={:08X}: {:08X}".format(self.total_iter, result))
        #return result.to_bytes(4,byteorder='big')
        return result

    def _decompress_header(self):
        """
        Decompress the first section of the compressed replay data.
        """

        # Maybe someday we'll have proper names for all of these ...
        r28_unk0, r28_unk1, r28_unk2, r28_unk3, r28_unk4, r24_loop1, = (0,)*6
        r31_loop1, r18_loop2, r25_loop3, r23_unk1 = (0,)*4
        r20_unk1 = 5

        self._decompress(8, header=True)
        self._decompress(7, header=True)
        self._decompress(6, header=True)
        self._decompress(32, header=True)
        self._decompress(32, header=True)
        r31_loop1 = self._decompress(5, header=True)
        self._decompress(3, header=True)
        self._decompress(2, header=True)
        self._decompress(1, header=True)
        self._decompress(7, header=True)

        while (r24_loop1 < r31_loop1):
            r28_unk0 = self._decompress(1, header=True)
            r28_unk0 = self._decompress(6, header=True)
            if (r20_unk1 > 3):
                r28_unk4 = self._decompress(5, header=True)
            if (r20_unk1 > 2):
                r28_unk3 = self._decompress(7, header=True)
            if (r28_unk0 != 0):
                r28_unk2 = self._decompress(2, header=True)
                if (r20_unk1 < 2):
                    r28_unk3 = self._decompress(7, header=True)
                if ((self._decompress(1) & 0x000000FF) != 0):
                    r18_loop2 = 0
                    while (r18_loop2 < 33216):
                        self._decompress(8, header=True)
                        r18_loop2 += 1
                r23_unk1 += 1
                r24_loop1 += 1
            elif (r28_unk0 == 0):
                r28_unk2 = 0
                r28_unk3 = 0
                r24_loop1 += 1

        if (r20_unk1 > 4):
            r25_loop3 = 0
            while (r25_loop3 < r24_loop1):
                self._decompress(1, header=True)
                r25_loop3 += 1

        r25_loop3 = 0
        while (r25_loop3 < r24_loop1):
            self._decompress(2, header=True)
            r25_loop3 += 1

        if (r20_unk1 >= 5):
            self._decompress(20, header=True)

    def _decompress_array(self):
        r20_loop1, r21_loop2, r19_loop3 = (0,)*3
        r4_unk1 = self._decompress(8, header=True)

        while (r20_loop1 < r4_unk1):
            self._decompress(14, header=True)
            self._decompress(14, header=True)
            self._decompress(4, header=True)
            self._decompress(5, header=True)
            self._decompress(5, header=True)
            self._decompress(5, header=True)
            self._decompress(5, header=True)
            self._decompress(5, header=True)

            r19_loop3 = 0
            r21_loop2 = 1
            while (r19_loop3 < r21_loop2):
                self._decompress(32, header=True)
                self._decompress(32, header=True)
                self._decompress(32, header=True)
                self._decompress(32, header=True)
                self._decompress(32, header=True)
                self._decompress(32, header=True)
                r19_loop3 += 1

            self._decompress(32, header=True)
            self._decompress(32, header=True)
            self._decompress(32, header=True)
            self._decompress(32, header=True)
            self._decompress(32, header=True)
            self._decompress(32, header=True)
            r20_loop1 += 1

        array_entries = self._decompress(14, header=True)
        self.replay_entries = array_entries

        for idx in range(array_entries + 1):
            mask =      self._decompress(8)
            strafe =    self._decompress(8)
            accel =     self._decompress(7)
            brake =     self._decompress(7)
            frames =    self._decompress(8)
            steer_x =   self._decompress(8)
            steer_y =   self._decompress(8)

            self.replay_array += mask.to_bytes(1, byteorder='big')
            self.replay_array += steer_x.to_bytes(1, byteorder='big')
            self.replay_array += steer_y.to_bytes(1, byteorder='big')
            self.replay_array += strafe.to_bytes(1, byteorder='big')
            self.replay_array += accel.to_bytes(1, byteorder='big')
            self.replay_array += brake.to_bytes(1, byteorder='big')
            self.replay_array += frames.to_bytes(1, byteorder='big')

class compressor(object):
    """
    The constructor needs references to all objects to-be-packed into the
    GCI. For now, we split this up into:

        * Some bytearray for header data. These are not arranged contiguously
          in memory, so we're just storing them as an array of 32 bit numbers,
          one for each call to `_decompress()`.

        * Some bytearray for the array of replay entry structures
    """

    def __init__(self, input_header):

        # A bytearray of 8-bit numbers (one for each call to `_compress()`).
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

        # The total number of iterations we've taken in `_decompress()`
        self.total_iter = 0

    def _compress(self, count, val, header=False, replay=False):
        result = 0
        #self.output += result.to_bytes(4, byteorder='big')
        num_iter = count
        if (num_iter == 0): return None
        while (count > 0):
            base_offset = (self.total_iter >> 3) & 0x1fffffff
            print("output_target={}".format(hex(self.output[base_offset])))
            if (base_offset < 0x8c000):
                mask = self.total_iter & 0x00000007
                if ( val & ( 1 << (num_iter - 1) ) != 0 ):
                        self.output[base_offset] = self.output[base_offset] | (1 << mask)
                self.total_iter += 1
                num_iter = num_iter - 1
                count = count - 1
        return self.output[base_offset]
