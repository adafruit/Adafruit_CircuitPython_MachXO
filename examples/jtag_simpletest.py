        # async_serial = tinyfpgaa.SyncSerial(ser)
        # pins = tinyfpgaa.JtagTinyFpgaProgrammer(async_serial)
        # jtag = tinyfpgaa.Jtag(pins)
        # programmer = tinyfpgaa.JtagCustomProgrammer(jtag)

        # if not args.q:
        #     if args.b:
        #         print("Parsing bitstream file...")
        #     else:
        #         print("Parsing JEDEC file...")

        # if args.b:
        #     input_file = tinyfpgaa.BitstreamFile(open(args.jed, 'rb'))
        # else:
        #     input_file = tinyfpgaa.JedecFile(open(args.jed, 'r'))

        # try:
        #     if not args.q:
        #         print("Programming TinyFPGA A on {}...".format(a_port))
        #     programmer.program(input_file)
