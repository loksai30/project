# Zero Dependency - Lossless Compression

This repository contains a compact zero-dependency implementation of a
lossless compressor following the team's modified master plan.

Features included in this branch:
- Interactive CLI with native file picker (tkinter)
- Huffman and RLE codecs
- Bit-level I/O utilities
- Custom .zc archive format with CRC32 and metadata
- Downloads-safe output naming
- Simple algorithm selection heuristic

Run:
    python run.py

This is a focused implementation intended to match the hackathon plan.
