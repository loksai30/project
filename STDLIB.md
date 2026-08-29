# Standard Library substitutions

This project intentionally avoids third-party runtime dependencies. Key
standard-library modules used and why:

- argparse / input() - CLI interaction
- tkinter + tkinter.filedialog - native file-selection dialog
- pathlib / os - filesystem operations and Downloads discovery
- collections.Counter - frequency counting
- heapq - Huffman priority queue
- struct - binary packing for the archive header
- zlib - CRC32 integrity
- time - timing/metrics
- unittest - testing (not included in this minimal push)
- tempfile - temporary files for tests

The plan requires the requirements.txt file to be empty; the runtime
relies only on Python's standard library.
