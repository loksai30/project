
class RLECodec:
    def encode(self, data: bytes) -> bytes:
        if not data:
            return b""
        out = bytearray()
        prev = data[0]
        count = 1
        for b in data[1:]:
            if b == prev and count < 255:
                count += 1
            else:
                out.append(count)
                out.append(prev)
                prev = b
                count = 1
        out.append(count)
        out.append(prev)
        return bytes(out)

    def decode(self, payload: bytes) -> bytes:
        out = bytearray()
        it = iter(payload)
        for c in it:
            # count
            val = c
            try:
                b = next(it)
            except StopIteration:
                raise ValueError("Invalid RLE payload: truncated pair")
            out.extend(bytes([b]) * val)
        return bytes(out)
