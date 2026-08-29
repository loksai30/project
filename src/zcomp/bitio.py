import struct

class BitWriter:
    def __init__(self):
        self.buffer = bytearray()
        self.acc = 0
        self.bits = 0

    def write_bit(self, bit: int):
        assert bit in (0,1)
        self.acc = (self.acc << 1) | bit
        self.bits += 1
        if self.bits == 8:
            self.buffer.append(self.acc)
            self.acc = 0
            self.bits = 0

    def write_bits(self, bits: str):
        for b in bits:
            self.write_bit(1 if b=='1' else 0)

    def get_bytes(self) -> bytes:
        if self.bits:
            # pad remaining bits on the right (least significant)
            self.acc <<= (8 - self.bits)
            self.buffer.append(self.acc)
        return bytes(self.buffer)


class BitReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.acc = 0
        self.bits = 0

    def read_bit(self):
        if self.bits == 0:
            if self.pos >= len(self.data):
                raise EOFError("no more bits")
            self.acc = self.data[self.pos]
            self.pos += 1
            self.bits = 8
        bit = (self.acc >> (self.bits-1)) & 1
        self.bits -= 1
        return bit

    def read_bits(self, n: int):
        out = []
        for _ in range(n):
            out.append(str(self.read_bit()))
        return ''.join(out)
