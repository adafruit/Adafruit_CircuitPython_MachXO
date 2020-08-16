from adafruit_bus_device import i2c_device

class _Register:
    def __init__(self, command, size):
        self._size = size
        self._buf = None
        self._command = command

    def __get__(self, instance, type):
        if self._buf is None:
            self._buf = bytearray(self._size)
        else:
            return self._buf
        with instance._bus as bus:
            bus.write_then_readinto(self._command, self._buf)
        return self._buf

class MachXO:
    device_id = _Register(b"\xE0\x00\x00\x00", 4)
    user_code = _Register(b"\x3C\x00\x00\x00", 4)
    feature_row = _Register(b"\xE7\x00\x00\x00", 8)
    feature_bits = _Register(b"\xFB\x00\x00\x00", 2)
    otp_fuses = _Register(b"\xFA\x00\x00\x00", 1)

    def __init__(self, bus, address=0x40):
        self.config_data = None
        self._bus = i2c_device.I2CDevice(bus, address)

        if self.device_id == b"\x61\x2B\xd0\x43":
            # Mach XO3 6900
            pass
        else:
            raise ValueError("Unable to confirm Mach XO device id")

        self._erased = False
        self._config_mode = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self._bus as bus:
            bus.write(b"\x5e\x00\x00\x00") # program done
            bus.write(b"\x79\x00\x00") # refresh

    def config_mode(self, offline=True):
        if self._config_mode:
            raise RuntimeError("Already in config mode")
        with self._bus as bus:
            bus.write(b"\xc6\x08\x00")
        self._config_mode = True
        return self

    def _check_config_mode(self,):
        if not self._config_mode:
            raise RuntimeError("Must be in config mode")

    def _wait_busy(self):
        buf = bytearray(1)
        buf[0] = 0x80
        cmd = b"\xf0\x00\x00\x00"
        while buf[0] & 0x80 != 0:
            with self._bus as bus:
                bus.write_then_readinto(cmd, buf)

    def erase(self, config_flash=True, user_flash=False, sram=False, feature_row=False):
        self._check_config_mode()
        cmd = bytearray(4)
        if user_flash and not any(config_flash, sram, feature_row):
            cmd[0] = 0xCB
        else:
            cmd[0] = 0x0E
            cmd[1] = 0x00
            if sram:
                cmd[1] |= 1 << 0
            if feature_row:
                cmd[1] |= 1 << 1
            if config_flash:
                cmd[1] |= 1 << 2
            if user_flash:
                cmd[1] |= 1 << 3
            cmd[2] = 0x00
            cmd[3] = 0x00
        with self._bus as bus:
            bus.write(cmd)
        self._wait_busy()
        self._erased = True


    def flash(self, data):
        self._check_config_mode()

        if not self._erased:
            self.erase()

        # Reset the configuration address
        with self._bus as bus:
            bus.write(b"\x46\x00\x00\x00")

        buf = bytearray(20)
        buf[0] = 0x70
        buf[3] = 0x01

        for page in data.get_config_pages():
            if len(page) != 16:
                raise RuntimeError("Incorrect page size")
            buf[4:] = page
            with self._bus as bus:
                bus.write(buf)
