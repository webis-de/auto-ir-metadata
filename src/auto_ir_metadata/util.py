import os
import urllib.request
from pathlib import Path

LIB_URL = "https://github.com/tira-io/measure/releases/download/v0.0.5/libmeasureapi.so"
LIB_FILE = Path(__file__).parent / 'libmeasureapi.so'


def ensure_so_is_available() -> Path:
    if not os.path.exists(LIB_FILE):
        urllib.request.urlretrieve(LIB_URL, LIB_FILE)

    return LIB_FILE


ensure_so_is_available()
