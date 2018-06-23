import os
import struct

class region:
    """
    Game ID bytes, corresponds to game region (4 bytes @ offset 0x00).
    """
    pal =   b'GFZP'
    jp =    b'GFZJ'
    ntsc =  b'GFZE'
    string = {  pal: "PAL",
                jp: "JP",
                ntsc: "NTSC", }
class ft:
    """
    Known filetype bytes (2 bytes @ offset 0x42)
    During runtime the game actually loads some data for parsing these which
    includes an "f_zero_debug" file with type b'\x00'. Not clear where this
    is actually accepted - might be vestigial or region-dependent?
    """
    replay =    b'\x05\x04'
    game =      b'\x01\x0b'
    ghost =     b'\x02\x01'
    garage =    b'\x03\x01'
    emblem =    b'\x04\x01'
    #debug =     b'\x00\x01'
    string = {  replay: "Replay file",
                game: "Gamedata file",
                garage: "Garage file",
                ghost: "Ghost file",
                emblem: "Emblem file", }

class machine():
    """
    Internal Machine IDs
    """
    blue_falcon     =  6
    deep_claw       =  7
    # ...

class gci(object):
    def __init__(self, filename=None, blocksize=None, gci_filename=None):
        """ Going to make this less confusing in the future, but: 'filename'
            is an existing GCI file that you want to read() into this object.
            Otherwise, pass 'gci_filename' and 'blocksize' to synthesize a new
            GCI (for F-Zero GX) with the given size/name. """

        if (filename is not None):
            self._filename = os.path.basename(filename).split(".")[0]
            self.raw_bytes = bytearray()
            try:
                self.fd = open(filename, "rb")
                self.filesize = os.stat(filename).st_size
                self.raw_bytes = bytearray(self.fd.read(self.filesize))
                self.fd.seek(0x0)
                print("Read {} bytes from input GCI".format(hex(self.filesize)))
            except FileNotFoundError as e:
                err(e)
                self.fd = None
                self.raw_bytes = None
                self.filesize = None
                return None
        else:
            if (blocksize < 0) or (blocksize is None):
                print("Need to specify blocksize when you aren't reading a GCI")
                return None
            if (gci_filename is None):
                print("Need to specify a GCI filename when you aren't reading a GCI")
                return None
            # Make a dentry
            self.raw_bytes = bytearray()
            self.raw_bytes += b'\x00'*0x40
            self.set_region(region.ntsc)
            self.set_maker_code()
            self.set_block_count(struct.pack(">H", blocksize))
            self.set_permissions(4)
            if (len(gci_filename) > 0x20):
                print("GCI filename must be <0x20 bytes long")
                return None
            if (len(gci_filename) < 0x20):
                fn_pad = gci_filename + ('\x00'*(0x20 - len(gci_filename)))
                self.set_filename(bytearray(fn_pad, 'ascii'))


    ''' These functions return other types '''

    def get_blocksize(self):
        return struct.unpack(">h", self.raw_bytes[0x38:0x3a])[0]
    def get_region(self):
        return region.strings[self.get_game_id()]
    def get_filetype(self):
        return ft.strings[self.get_filetype_bytes()]

    ''' These functions return raw bytes '''

    def dump(self):
        return self.raw_bytes
    def get_dentry(self):
        return self.raw_bytes[0:0x40]

    def get_game_id(self):
        return self.raw_bytes[0x00:0x04]
    def get_maker_code(self):
        return self.raw_bytes[0x04:0x06]
    def get_filename(self):
        return self.raw_bytes[0x08:0x28]
    def get_modtime(self):
        return self.raw_bytes[0x28:0x2c]
    def get_image_off(self):
        return self.raw_bytes[0x2c:0x30]
    def get_icon_fmt(self):
        return self.raw_bytes[0x30:0x32]
    def get_anim_speed(self):
        return self.raw_bytes[0x32:0x34]
    def get_permissions(self):
        return self.raw_bytes[0x34:0x35]
    def get_copy_ctr(self):
        return self.raw_bytes[0x35:0x36]
    def get_first_block(self):
        return self.raw_bytes[0x36:0x38]
    def get_block_count(self):
        return self.raw_bytes[0x38:0x3a]
    #def get_unused_word(self):
    #   return self.raw_bytes[0x3a:0x3c]
    def get_block_count(self):
        return self.raw_bytes[0x38:0x3a]
    def get_comment_addr(self):
        return self.raw_bytes[0x3c:0x40]

    def get_checksum(self):
        return self.raw_bytes[0x40:0x42]
    def get_filetype_bytes(self):
        return self.raw_bytes[0x42:0x44]

    # Banner/icon data lives from 0x42 to 0x20a0.

    def get_replay_data_len(self):
        return len(self.raw_bytes[0x20a0:])
    def get_replay_data(self):
        return self.raw_bytes[0x20a0:]

    ''' These functions take a `bytearray()` and replace some field '''

    def set_filename(self, new_filename):
        self.raw_bytes[0x08:0x28] = new_filename
    def set_modtime(self, new_modtime):
        self.raw_bytes[0x28:0x2c] = struct.pack(">L", new_modtime)
    def set_filetype(self, new_filetype):
        self.raw_bytes[0x42:0x44] = bytearray(new_filetype)
    def set_block_count(self, new_bc):
        self.raw_bytes[0x38:0x3a] = new_bc
    def set_comment_addr(self, new_addr):
        self.raw_bytes[0x3c:0x40] = new_addr
    def set_region(self, new_gameid):
        self.raw_bytes[0x00:0x04] = bytearray(new_gameid)
    def set_maker_code(self):
        self.raw_bytes[0x04:0x06] = bytearray(b'8P') # ?
    def set_permissions(self, new_perm):
        self.raw_bytes[0x34:0x35] = struct.pack(">B", new_perm)
    def set_checksum(self, new_checksum):
        """ Expects some packed bytes (>H) """
        self.raw_bytes[0x40:0x42] = new_checksum
    def set_replay_data(self, new_replay_data):
        """
        Replace the current replay data with some new replay data.
        new_replay_data should be a bytearray() of the appropriate size.
        """
        original_replay_data_len = self.get_replay_data_len()
        self.raw_bytes[0x20a0:] = new_replay_data[:original_replay_data_len]

    def recompute_checksum(self):
        """
        Recompute the checksum over the GCI, writing in the new checksum if
        the value has changed at all
        """
        current_checksum = struct.unpack(">H", self.get_checksum())[0]
        new_checksum = 0xFFFF
        data = self.raw_bytes[0x42:]
        for byte in data:
            new_checksum = new_checksum ^ byte
            for j in range(8):
                if ((new_checksum & 1) == 1):
                    new_checksum = (new_checksum >> 1) ^ 0x8408
                else:
                    new_checksum = new_checksum >> 1
        new_checksum = new_checksum ^ 0xFFFF
        if (current_checksum == new_checksum):
            print("Checksum values are the same! [{}]".format(hex(new_checksum)))
        else:
            print("Recomputed checksum [{}] -> [{}]".format(hex(current_checksum),
                                                            hex(new_checksum)))
            self.set_checksum(struct.pack(">H", new_checksum))
