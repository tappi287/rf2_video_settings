import os
import logging
import sys
from pathlib import Path
from typing import Union

from appdirs import user_data_dir, user_log_dir


logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)

APP_NAME = 'rf2_settings_widget'
SETTINGS_DIR_NAME = 'rf2_settings_widget'
SETTINGS_FILE_NAME = 'settings.json'
PRESETS_DIR = 'presets'
APP_FRIENDLY_NAME = 'rF2 Settings Widget'
BASE_PATH = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__ + '/..')))
RFACTOR_PLAYER = 'UserData/player/player.JSON'
RFACTOR_DXCONFIG = 'UserData/Config_DX11.ini'

DEFAULT_LOG_LEVEL = 'DEBUG'

# Frozen or Debugger
if getattr(sys, 'frozen', False):
    # -- Running in PyInstaller Bundle ---
    FROZEN = True
else:
    # -- Running in IDE ---
    FROZEN = False


def check_and_create_dir(directory: Union[str, Path]) -> str:
    if not os.path.exists(directory):
        try:
            os.mkdir(directory)
            logging.info('Created: %s', directory)
        except Exception as e:
            logging.error('Error creating directory %s', e)
            return ''

    return directory


def get_current_modules_dir() -> str:
    """ Return path to this app modules directory """
    return BASE_PATH


def get_settings_dir() -> Path:
    return Path(check_and_create_dir(user_data_dir(SETTINGS_DIR_NAME, '')))


def get_presets_dir() -> Path:
    settings_dir = get_settings_dir()
    return Path(check_and_create_dir(settings_dir / PRESETS_DIR))


def get_log_dir() -> str:
    log_dir = user_log_dir(SETTINGS_DIR_NAME, '')
    setting_dir = os.path.abspath(os.path.join(log_dir, '../'))
    # Create <app-name>
    check_and_create_dir(setting_dir)
    # Create <app-name>/log
    return check_and_create_dir(log_dir)
