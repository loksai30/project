import time
from contextlib import contextmanager

@contextmanager
def timeit(label: str = None):
    t0 = time.perf_counter()
    try:
        yield lambda: None
    finally:
        t1 = time.perf_counter()
        if label:
            print(f"{label}: {t1-t0:.4f}s")
