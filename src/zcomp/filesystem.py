from pathlib import Path
import os
import sys

def downloads_path():
    # heuristics for Downloads folder
    home = Path.home()
    candidates = [home / 'Downloads']
    if sys.platform == 'win32':
        # common fallback
        candidates.append(home / 'Downloads')
    for p in candidates:
        if p.exists():
            return p
    return home


def safe_output_path(dest_dir: Path, base_name: str) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    p = dest_dir / base_name
    if not p.exists():
        return p
    # add (n) suffix
    stem = p.stem
    suffix = p.suffix
    i = 1
    while True:
        candidate = dest_dir / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1
