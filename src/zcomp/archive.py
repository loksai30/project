"""Archive writer/reader for .zc format

Format (simple MVP):
- 4 bytes magic: b'ZC\x00' + version
- 1 byte version
- 1 byte algorithm id (1=Huffman,2=RLE)
- 2 bytes flags (reserved)
- 8 bytes original size (uint64)
- 4 bytes crc32 (uint32)
- 4 bytes metadata length (uint32)
- metadata (JSON, UTF-8)
- payload (raw bytes)

Metadata currently carries the original filename and algorithm-specific
structures (e.g., frequency table for Huffman).
"""

import struct
import json
import zlib
from pathlib import Path
from .errors import ArchiveError

MAGIC = b"ZC\x01"
VERSION = 1
ALG_HUFFMAN = 1
ALG_RLE = 2

class ZCArchive:
    def create(self, data: bytes, filename: str, algorithm: int, codec_meta: dict, payload: bytes) -> bytes:
        orig_size = len(data)
        crc = zlib.crc32(data) & 0xffffffff
        meta = {
            "filename": Path(filename).name,
            "codec_meta": codec_meta,
        }
        meta_bytes = json.dumps(meta, separators=(',',':')).encode('utf-8')
        header = bytearray()
        header.extend(MAGIC)
        header.extend(struct.pack('<B', VERSION))
        header.extend(struct.pack('<B', algorithm))
        header.extend(struct.pack('<H', 0))
        header.extend(struct.pack('<Q', orig_size))
        header.extend(struct.pack('<I', crc))
        header.extend(struct.pack('<I', len(meta_bytes)))
        return bytes(header) + meta_bytes + payload

    def parse(self, blob: bytes):
        # minimal validations
        if len(blob) < 4+1+1+2+8+4+4:
            raise ArchiveError("archive truncated or too small")
        if blob[0:4] != MAGIC:
            raise ArchiveError("bad magic")
        pos = 4
        version = blob[pos]
        if version != VERSION:
            raise ArchiveError("unsupported version")
        pos += 1
        alg = blob[pos]
        pos += 1
        flags = struct.unpack('<H', blob[pos:pos+2])[0]
        pos += 2
        orig_size = struct.unpack('<Q', blob[pos:pos+8])[0]
        pos += 8
        crc = struct.unpack('<I', blob[pos:pos+4])[0]
        pos += 4
        meta_len = struct.unpack('<I', blob[pos:pos+4])[0]
        pos += 4
        if len(blob) < pos + meta_len:
            raise ArchiveError("metadata truncated")
        meta_bytes = blob[pos:pos+meta_len]
        pos += meta_len
        try:
            meta = json.loads(meta_bytes.decode('utf-8'))
        except Exception as e:
            raise ArchiveError("invalid metadata JSON") from e
        payload = blob[pos:]
        return {
            'algorithm': alg,
            'flags': flags,
            'original_size': orig_size,
            'crc': crc,
            'meta': meta,
            'payload': payload,
        }

    def verify_and_extract(self, blob: bytes):
        parsed = self.parse(blob)
        alg = parsed['algorithm']
        meta = parsed['meta']
        orig_size = parsed['original_size']
        crc_expected = parsed['crc']
        payload = parsed['payload']
        codec_meta = meta.get('codec_meta', {})
        # decode
        if alg == ALG_RLE:
            from .rle import RLECodec
            out = RLECodec().decode(payload)
        elif alg == ALG_HUFFMAN:
            from .huffman import HuffmanCodec
            freq = {int(k):v for k,v in codec_meta.get('freq', {}).items()} if codec_meta else {}
            out = HuffmanCodec().decode(payload, freq, orig_size)
        else:
            raise ArchiveError("unknown algorithm")
        # verify size and crc
        if len(out) != orig_size:
            raise ArchiveError("decoded size mismatch")
        crc = zlib.crc32(out) & 0xffffffff
        if crc != crc_expected:
            raise ArchiveError("crc mismatch")
        return meta.get('filename', 'output'), out
