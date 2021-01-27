import logging
import platform
import sys
import webbrowser

import eel

from webmethods import expose_methods
from rf2settings.app_settings import AppSettings
from rf2settings.runasadmin import run_as_admin


logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)

# TODO: -Proper- logging setup
# TODO: Video Settings Windowed/Borderless/Fullscreen switch


def start_eel():
    AppSettings.load()
    AppSettings.copy_default_presets()

    # This will ask for and re-run with admin rights
    # if setting needs_admin set.
    if AppSettings.needs_admin and not run_as_admin():
        return

    """
        THIS WILL DISABLE ctypes support! But it will make sure "Launch rFactor2" 
        or basically any executable that is loading DLLs will work.
    """
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.SetDllDirectoryA(None)
    """
        //
    """

    host = 'localhost'
    port = 8123
    eel.init('web')

    try:
        eel.start('index.html', size=(960, 600), host=host, port=port)
    except EnvironmentError:
        # If Chrome isn't found, fallback to Microsoft Edge on Win10 or greater
        if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:
            eel.start('index.html', size=(960, 600), mode='edge', host=host, port=port)
        # Fallback to opening a regular browser window
        else:
            eel.start('index.html', size=(960, 600), mode=None, app_mode=False, host=host, port=port, block=False)
            # Open system default web browser
            webbrowser.open_new(f'http://{host}:{port}')
            # Run until window/tab closed
            while True:
                eel.sleep(10.0)


if __name__ == '__main__':
    expose_methods()
    start_eel()
