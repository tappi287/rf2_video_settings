import ctypes
from pathlib import Path, WindowsPath

from rf2settings.rfactor import RfactorPlayer

PLUGIN_NAME = "ChatTransceiver"


def main():
    rf = RfactorPlayer()
    plugin_dir = rf.location / "Bin64" / "Plugins"
    if not plugin_dir.exists():
        return

    plugin_path = plugin_dir / f'{PLUGIN_NAME}.dll'
    if not plugin_path.exists() and plugin_path.is_file():
        return

    plugin_lib = ctypes.cdll.LoadLibrary(str(WindowsPath(plugin_path)))
    send_message = plugin_lib.send_message
    send_message.argtypes = [ctypes.c_char_p]
    send_message.restype = ctypes.c_bool
    result = send_message(ctypes.c_char_p("Hello World bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla 123456789 ÄÜÖ##sdsds bla bla bla bla bla bla bla bla".encode('ascii')))
    print("Result:", result)


if __name__ == '__main__':
    main()
