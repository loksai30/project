"""Zero-Dependency - Zero Compress package

Minimal implementation following the provided master plan.
This package implements:
- BitWriter / BitReader
- Huffman codec (simple frequency-table metadata)
- RLE codec
- .zc archive writer/reader
- CLI app with tkinter file dialogs
- Downloads-safe output handling

This is intentionally compact to be readable and to serve as a working
reference for the hackathon plan.
"""

from .bitio import BitWriter, BitReader
from .huffman import HuffmanCodec
from .rle import RLECodec
from .archive import ZCArchive
from .filesystem import downloads_path, safe_output_path
from .metrics import timeit
from .file_dialog import select_file_for_compress, select_file_for_decompress
from .errors import ArchiveError

__all__ = [
    "BitWriter",
    "BitReader",
    "HuffmanCodec",
    "RLECodec",
    "ZCArchive",
    "downloads_path",
    "safe_output_path",
    "timeit",
    "select_file_for_compress",
    "select_file_for_decompress",
    "ArchiveError",
]
