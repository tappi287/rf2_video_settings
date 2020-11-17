import sys
import logging

import eel

from modules.app_settings import AppSettings

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)

# TODO: -Proper- logging setup
# TODO: Video Settings Windowed/Borderless/Fullscreen switch
# TODO: Edge launcher
# TODO: Preset drag drop import
# TODO: save Presets in user myDocs dir, differentiate between app defaults and user saved presets


def start_eel():
    AppSettings.load()

    # register exposed methods
    from modules.web import message, get_presets, select_preset, save_preset, delete_preset
    eel.init('web')
    eel.start('index.html', size=(960, 600))

    if 'fake_use_imports' == '':
        print(message, get_presets, select_preset, save_preset, delete_preset)


if __name__ == '__main__':
    start_eel()
