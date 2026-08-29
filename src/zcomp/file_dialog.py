from tkinter import Tk, filedialog
from pathlib import Path

def _ask_file_dialog(title: str, filetypes=None):
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()
    if not path:
        return None
    p = Path(path)
    if not p.exists() or not p.is_file():
        return None
    return p


def select_file_for_compress():
    return _ask_file_dialog('Select file to compress')


def select_file_for_decompress():
    return _ask_file_dialog('Select .zc archive to decompress', filetypes=[('Zero-Compress','.zc'),('All files','*.*')])
