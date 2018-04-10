

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

    def get_region(x):
        """
        Given some raw game ID bytes, return the corresponding string
        """

        if x in region.string:
            return "{} ({})".format(region.string.get(x), x.hex())
        else:
            return "Unknown ({})".format(x)

class ft:
    """
    Known filetype bytes (2 bytes @ offset 0x42).
    """

    replay =    b'\x05\x04'
    game =      b'\x01\x0b'
    ghost =     b'\x02\x01'
    garage =    b'\x03\x01'
    emblem =    b'\x04\x01'

    string = {  replay: "Replay file",
                game: "Gamedata file",
                garage: "Garage file",
                ghost: "Ghost file",
                emblem: "Emblem file", }

    def get_filetype(x):
        """
        Given some raw filetype bytes, return the corresponding string
        """

        if x in ft.string:
            return "{} ({})".format(ft.string.get(x), x.hex())
        else:
            return "Unknown ({})".format(x.hex())
