import ctypes
import json
import time

from auto_ir_metadata.util import ensure_so_is_available


class MapiConfig(ctypes.Structure):
    _fields_ = [("provider", ctypes.POINTER(ctypes.c_char_p)),
                ("monitor", ctypes.c_bool),
                ("pollintervall_ms", ctypes.c_size_t)]

class MapiResultEntry(ctypes.Structure):
    _fields_ = [("name", ctypes.c_char_p),
                ("value", ctypes.POINTER(None))]

@ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p)
def log_callback(level: ctypes.c_int, component: ctypes.c_char_p, message: ctypes.c_char_p) -> None:
    """
    Implements a simple logger callback that can be fed to mapiSetLogCallback.
    """
    level_to_name = ["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
    print(f"[{component.decode('ascii')}] [{level_to_name[level]}] {message.decode('ascii')}")

def result_to_dict(lib, result: ctypes.POINTER(None)) -> str | dict:
    """
    Takes a reference to the library and a pointer to a results object and recursively translates it into a python object.
    """
    value = ctypes.c_char_p()
    if (lib.mapiResultGetValue(result, ctypes.pointer(value))):
        return value.value.decode('ascii')
    else:
        num = lib.mapiResultGetEntries(result, None, 0)
        buf = (MapiResultEntry*num)()
        lib.mapiResultGetEntries(result, buf, num)
        return {entry.name.decode('ascii'): result_to_dict(lib, entry.value) for entry in buf}


def measure():
    libmeasureapi = ctypes.cdll.LoadLibrary(ensure_so_is_available())
    print(libmeasureapi)


    # (Optional): Register logger
    libmeasureapi.mapiSetLogCallback(log_callback)

    providers = [b"git"]
    providers_native = (ctypes.c_char_p*len(providers))(*providers)
    config = MapiConfig(providers_native, True, 100)
    handle = libmeasureapi.mapiStartMeasure(config)

    # Step 3: Run your code
    time.sleep(2)

    libmeasureapi.mapiStopMeasure(handle)
    # Step 4: Stop measuring and fetch a handle to the result (needs to be freed by us later!)
    # result = libmeasureapi.mapiStopMeasure(handle)
    # obj = result_to_dict(libmeasureapi, result)

    # Step 5: Cleanup, delete the result from memory
    # libmeasureapi.mapiResultFree(result)

    # Step 6..N: Do what you want
    # print(json.dumps(obj, indent=2))


if __name__ == "__main__":
    measure()
