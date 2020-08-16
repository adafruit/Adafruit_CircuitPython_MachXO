import adafruit_jtag
import board
import digitalio

tck = digitalio.DigitalInOut(board.D5)
tms = digitalio.DigitalInOut(board.D6)
tdi = digitalio.DigitalInOut(board.D9)
tdo = digitalio.DigitalInOut(board.D10)
jtag = adafruit_jtag.Jtag(tck=tck, tms=tms, tdi=tdi, tdo=tdo)

buf = bytearray(32)

# Read th
jtag.write_ir(8, 0xE0)
jtag.read_dr(32, buf)
print(buf[:4])

# Set the boundary conditions.
jtag.write_ir(8, 0x1c)
jtag.write_dr(664, True)


# Shift in LSC_READ_STATUS(0x3C) instruction
jtag.write_ir(8, 0x3c)
jtag.runtest(2)
jtag.read_dr(32, buf)
print("status", buf[:4])

# Enable the Flash

# Shift in ISC ENABLE(0xC6) instruction
jtag.write_ir(8, 0xc6)
jtag.write_dr(8, 0x00)
jtag.runtest(2)

# Shift in ISC ERASE(0x0E) instruction
jtag.write_ir(8, 0x0e)
jtag.write_dr(8, 0x01)
jtag.runtest(2)

# Shift in BYPASS(0xFF) instruction
jtag.write_ir(8, 0xff)

# Shift in ISC ENABLE(0xC6) instruction
jtag.write_ir(8, 0xc6)
jtag.write_dr(8, 0x08)
jtag.runtest(2)

# Shift in LSC_READ_STATUS(0x3C) instruction
jtag.write_ir(8, 0x3c)
jtag.runtest(2)
jtag.read_dr(32, buf)
print("status", buf[:4])

jtag.write_ir(8, 0x0e)
jtag.write_dr(8, 0x0e)
jtag.runtest(2)

# Shift in LSC_CHECK_BUSY(0xF0) instruction
jtag.write_ir(8, 0xf0)

# Wait for busy
i = 0
while True:
        jtag.runtest(2)
        jtag.read_dr(1, buf)
        if buf[0] == 0:
                print("done", i)
                break
        i += 1

jtag.write_ir(8, 0x26)
jtag.runtest(2)

# Shift in BYPASS(0xFF) instruction
jtag.write_ir(8, 0xff)
jtag.runtest(100)

jtag.goto_state("RESET")
