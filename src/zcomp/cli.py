"""Simple CLI application glue"""
from pathlib import Path
import argparse
import sys
import json
import zlib
from .filesystem import downloads_path, safe_output_path
from .huffman import HuffmanCodec
from .rle import RLECodec
from .archive import ZCArchive, ALG_HUFFMAN, ALG_RLE
from .file_dialog import select_file_for_compress, select_file_for_decompress
from .metrics import timeit
from .errors import ArchiveError


def compress_flow():
    p = select_file_for_compress()
    if p is None:
        print('No file selected.')
        return
    data = p.read_bytes()
    # Choose algorithm -- simple heuristic from the provided table
    alg = choose_algorithm(p, data)
    if alg == ALG_HUFFMAN:
        codec = HuffmanCodec()
        payload, freq = codec.encode(data)
        codec_meta = {'freq': {str(k):v for k,v in freq.items()}}
    else:
        codec = RLECodec()
        payload = codec.encode(data)
        codec_meta = {}
    archive = ZCArchive().create(data, p.name, alg, codec_meta, payload)
    downloads = downloads_path()
    out_path = safe_output_path(downloads, p.with_suffix('.zc').name)
    out_path.write_bytes(archive)
    print('Done!')
    print('Original size:', len(data))
    print('Archive size:', out_path.stat().st_size)
    print('Saved to:', out_path)


def choose_algorithm(path: Path, data: bytes):
    # Heuristic using file extension and repetitiveness
    ext = path.suffix.lower()
    if ext in ('.txt', '.md', '.py', '.json', '.csv', '.xml'):
        return ALG_HUFFMAN
    # if very repetitive favor RLE
    if len(data) > 0:
        from collections import Counter
        top = Counter(data).most_common(1)[0][1]
        if top / max(1,len(data)) > 0.5:
            return ALG_RLE
    return ALG_HUFFMAN


def decompress_flow():
    p = select_file_for_decompress()
    if p is None:
        print('No file selected.')
        return
    blob = p.read_bytes()
    try:
        name, data = ZCArchive().verify_and_extract(blob)
    except ArchiveError as e:
        print('Archive error:', e)
        return
    downloads = downloads_path()
    out_path = safe_output_path(downloads, name)
    out_path.write_bytes(data)
    print('Decompressed and saved to:', out_path)


def main():
    print('========================================')
    print('   ZERO-COMPRESS - LOSSLESS FILE TOOL')
    print('========================================')
    while True:
        print('\nWhat would you like to do?\n')
        print('1. Compress a file')
        print('2. Decompress a .zc file')
        print('3. Exit')
        choice = input('Select an option: ').strip()
        if choice == '1':
            compress_flow()
        elif choice == '2':
            decompress_flow()
        elif choice == '3':
            print('Goodbye')
            return
        else:
            print('Invalid choice')


if __name__ == '__main__':
    main()
