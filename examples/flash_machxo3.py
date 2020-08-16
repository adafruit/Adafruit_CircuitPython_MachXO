import board

i2c = board.I2C()

i2c.try_lock()
print([hex(x) for x in i2c.scan()])
i2c.unlock()

import adafruit_machxo

from adafruit_machxo import bitstream

fpga = adafruit_machxo.MachXO(i2c)
print("".join(["{:02x}".format(x) for x in fpga.device_id]))

config = None
bitfile = open("top.bit", "rb")
config = bitstream.BitstreamFile(bitfile)

with fpga.config_mode():
    fpga.erase()
    fpga.flash(config)
