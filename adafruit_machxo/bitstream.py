# SPDX-FileCopyrightText: 2020 Luke Valenty for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense


class BitstreamFile:
    def __init__(self, bit_file):
        self.cfg_data = None
        self.ebr_data = None
        self.ufm_data = None
        self.feature_row = None
        self.feature_bits = None
        self.last_note = ""
        self._file = bit_file

    def numRows(self):
        def toInt(list_or_none):
            if list_or_none is None:
                return 0
            else:
                return len(list_or_none)

        return toInt(self.cfg_data) + toInt(self.ebr_data) + toInt(self.ufm_data)

    def get_config_pages(self):
        bit = self._file
        bit.seek(0)
        # Validate we have a bitstream.
        header = bit.read(2)
        if header != b"\xff\x00":
            raise ValueError("Bitstream file does not begin with 0xFF00.")

        ff_count = 0
        while True:
            val = bit.read(1)
            if val == b"\xff":
                ff_count += 1
            elif val == b"\xbd" and ff_count >= 2:
                val4 = bit.read(1)
                if val4 == b"\xb3":
                    break
                ff_count = 0
            else:
                ff_count = 0
            if not val:
                raise ValueError("Could not find bitstream preamble.")

        start_of_data = bit.tell() - 4

        # Eat characters and commands until we find a compressed bitstream.
        while True:
            cmd = bit.read(1)

            # BYPASS
            if cmd == b"\xff":
                pass
            # LSC_RESET_CRC
            elif cmd == b"\x3b":
                bit.read(3)
            # VERIFY_ID
            elif cmd == b"\xe2":
                bit.read(7)
            # LSC_WRITE_COMP_DIC
            elif cmd == b"\x02":
                bit.read(11)
            # LSC_PROG_CNTRL0
            elif cmd == b"\x22":
                bit.read(7)
            # LSC_INIT_ADDRESS
            elif cmd == b"\x46":
                bit.read(3)
            # LSC_PROG_INCR_CMP
            elif cmd == b"\xb8":
                break
            # LSC_PROG_INCR_RTI
            elif cmd == b"\x82":
                raise ValueError("Bitstream is not compressed- not writing.")
            else:
                assert False, "Unknown command type {}.".format(cmd)

        bit.seek(start_of_data)

        done = False
        while not done:
            line = bit.read(16)

            if len(line) < 16:
                line = line + b"\xff" * (16 - len(line))
                done = True

            yield line
