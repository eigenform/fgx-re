

class decompressor(object):
    """
    This object has to keep track of three things:
        * The number of bits (?) we've decoded
        * The input data buffer (a bytearray)
        * The output data buffer (a bytearray)
    """
    def __init__(self, compressed_data ):
        self.input = compressed_data
        self.output = bytearray()
        self.total_iter = 0

    def _decompress(self, count):
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

        # In one sense, we want 32-bit output because the compression
        # function operates on a whole 32-bit register.
        self.output += result.to_bytes(4, byteorder='big')
        #
        # But in another sense, the actual bits of the result used by other
        # functions seems to vary; the high-level decompression functions
        # usually mask away bits before writing them somewhere in memory
        # during decompression.
        #self.output += result.to_bytes(((result.bit_length() + 7) // 8), byteorder='big')

        print("iter={:08X}: {:08X}".format(self.total_iter, result))
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

        self._decompress(8)
        self._decompress(7)
        self._decompress(6)
        self._decompress(32)
        self._decompress(32)
        r31_loop1 = self._decompress(5)
        self._decompress(3)
        self._decompress(2)
        self._decompress(1)
        self._decompress(7)

        while (r24_loop1 < r31_loop1):
            r28_unk0 = self._decompress(1)
            r28_unk0 = self._decompress(6)
            if (r20_unk1 > 3):
                r28_unk4 = self._decompress(5)
            if (r20_unk1 > 2):
                r28_unk3 = self._decompress(7)
            if (r28_unk0 != 0):
                r28_unk2 = self._decompress(2)
                if (r20_unk1 < 2):
                    r28_unk3 = self._decompress(7)
                if ((self._decompress(1) & 0x000000FF) != 0):
                    r18_loop2 = 0
                    while (r18_loop2 < 33216):
                        self._decompress(8)
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
                self._decompress(1)
                r25_loop3 += 1

        r25_loop3 = 0
        while (r25_loop3 < r24_loop1):
            self._decompress(2)
            r25_loop3 += 1

        if (r20_unk1 >= 5):
            self._decompress(20)

    def _decompress_array(self):
        r20_loop1, r21_loop2, r19_loop3 = (0,)*3
        r4_unk1 = self._decompress(8)

        while (r20_loop1 < r4_unk1):
            self._decompress(14)
            self._decompress(14)
            self._decompress(4)
            self._decompress(5)
            self._decompress(5)
            self._decompress(5)
            self._decompress(5)
            self._decompress(5)

            r19_loop3 = 0
            r21_loop2 = 1
            while (r19_loop3 < r21_loop2):
                self._decompress(32)
                self._decompress(32)
                self._decompress(32)
                self._decompress(32)
                self._decompress(32)
                self._decompress(32)
                r19_loop3 += 1

            self._decompress(32)
            self._decompress(32)
            self._decompress(32)
            self._decompress(32)
            self._decompress(32)
            self._decompress(32)
            r20_loop1 += 1

        array_entries = self._decompress(14)

        # Loop for the array is actually here:
        # ...
