import sys
import platform
import logging
import webbrowser

import eel

from modules.app_settings import AppSettings

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)

# TODO: -Proper- logging setup
# TODO: Video Settings Windowed/Borderless/Fullscreen switch
# TODO: detect need for Admin rights during backup
# TODO: JS close method


def start_eel():
    AppSettings.load()
    AppSettings.copy_default_presets()

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
            webbrowser.open_new(f'http://{host}:{port}')
            while True:
                eel.sleep(10.0)


if __name__ == '__main__':
    start_eel()
