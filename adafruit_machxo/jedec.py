
class JedecFile(object):
    def __init__(self, jed_file):
        self.cfg_data = None
        self.ebr_data = None
        self.ufm_data = None
        self.feature_row = None
        self.feature_bits = None
        self.last_note = ""
        self._parse(jed_file)

    def numRows(self):
        def toInt(list_or_none):
            if list_or_none is None:
                return 0
            else:
                return len(list_or_none)

        return toInt(self.cfg_data) + toInt(self.ebr_data) + toInt(self.ufm_data)

    def _parse(self, jed):
        def line_to_int(line):
            try:
                return int(line[::-1], 2)
            except:
                traceback.print_exc()
                return None

        def line_is_end_of_field(line):
            return "*" in line

        def line_is_end_of_file(line):
            return r"\x03" in line

        def process_field(field):
            if field[0][0:4] == "NOTE":
                self.last_note = field[0][5:-1]

            elif field[0][0] == "L":
                data = []

                for fuse_string in field[1:-1]:
                    fuse_data = line_to_int(fuse_string)

                    if fuse_data is not None:
                        data.append(fuse_data)

                if "EBR_INIT DATA" in self.last_note:
                    self.ebr_data = data

                elif "END CONFIG DATA" in self.last_note:
                    pass # ignore this data

                elif "TAG DATA" in self.last_note:
                    self.ufm_data = data

                else:
                    self.cfg_data = data

            elif field[0][0] == "E":
                self.feature_row = line_to_int(field[0][1:])
                self.feature_bits = line_to_int(field[1][:-1])



        lines = iter(jed)

        try:
            line = next(lines).strip()

            while True:
                current_field = [line]

                while not line_is_end_of_field(line):
                    line = next(lines).strip()
                    current_field.append(line)

                process_field(current_field)

                line = next(lines).strip()

        except StopIteration:
            pass
