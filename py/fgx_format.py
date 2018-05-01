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
    Known filetype bytes (2 bytes @ offset 0x42).
    """
    replay =    b'\x05\x04'
    game =      b'\x01\x0b'
    ghost =     b'\x02\x01'
    garage =    b'\x03\x01'
    emblem =    b'\x04\x01'
    debug =     b'\x00\x01' # takes sys_e.bin like a save file???
    string = {  replay: "Replay file",
                game: "Gamedata file",
                garage: "Garage file",
                ghost: "Ghost file",
                emblem: "Emblem file", }

class machine():
    """
    Machine IDs
    """
    blue_falcon     =  6
    deep_claw       =  7


class gci(object):
    def __init__(self, filename):
        self._filename = os.path.basename(filename).split(".")[0]
        self.raw_bytes = bytearray()
        try:
            self.fd = open(filename, "rb")
            self.filesize = os.stat(filename).st_size
            self.raw_bytes = bytearray(self.fd.read(self.filesize))
            self.fd.seek(0x0)
            print("[*] Read {} bytes from {}".format(hex(self.filesize), filename))
        except FileNotFoundError as e:
            err(e)
            self.fd = None
            self.raw_bytes = None
            self.filesize = None
            return None

    ''' These functions return other types '''
    def get_blocksize(self):
        return struct.unpack(">h", self.raw_bytes[0x38:0x3a])[0]
    def get_region(self):
        return region.strings[self.get_game_id()]
    def get_filetype(self):
        return ft.strings[self.get_filetype_bytes()]
    ''' These functions return raw bytes '''
    def get_game_id(self):
        return self.raw_bytes[0x00:0x04]
    def get_filename(self):
        return self.raw_bytes[0x08:0x28]

    # modtime 0x28:0x2c
    # image off 0x2c:0x30
    # icon_fmt 0x30:0x32
    # anim speed 0x32:0x34
    # permissions 0x34:0x35
    # copy_ctr 0x35:0x36
    # first_block 0x36:0x38
    # block_count 0x38:0x3a
    # unused 0x3a:0x3c

    def get_block_count(self):
        return self.raw_bytes[0x38:0x3a]
    def get_comment_addr(self):
        return self.raw_bytes[0x3c:0x40]

    def get_filetype_bytes(self):
        return self.raw_bytes[0x42:0x44]
    def get_checksum(self):
        return self.raw_bytes[0x40:0x42]
    def get_dentry(self):
        return self.raw_bytes[0:0x40]
    def get_replay_data(self):
        return self.raw_bytes[0x20a0:]
    def get_replay_data_len(self):
        return len(self.raw_bytes[0x20a0:])
    def dump(self):
        return self.raw_bytes

    def set_filename(self, new_filename):
        self.raw_bytes[0x08:0x28] = new_filename
    def set_filetype(self, new_filetype):
        self.raw_bytes[0x42:0x44] = bytearray(new_filetype)

    def set_block_count(self, new_bc):
        self.raw_bytes[0x38:0x3a] = new_bc
    def set_comment_addr(self, new_addr):
        self.raw_bytes[0x3c:0x40] = new_addr

    def set_region(self, new_gameid):
        self.raw_bytes[0x00:0x04] = bytearray(new_gameid)

    def set_checksum(self, new_checksum):
        """ Expects some packed bytes (>H) """
        self.raw_bytes[0x40:0x42] = new_checksum

    def set_replay_data(self, new_replay_data):
        """
        Replace the current replay data with some new replay data.
        new_replay_data should be a bytearray().
        """
        original_replay_data_len = self.get_replay_data_len()
        self.raw_bytes[0x20a0:] = new_replay_data[:original_replay_data_len]

    def recompute_checksum(self):
        """
        Recompute the checksum over the GCI, writing in the new checksum
        if the value has changed at all
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
