import os
import logging
import sys
import json
from pathlib import Path
from typing import Union

from appdirs import user_data_dir, user_log_dir


logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)

APP_NAME = 'rf2_settings_widget'
SETTINGS_DIR_NAME = 'rf2_settings_widget'
EXPORT_DIR_NAME = 'exported'
SETTINGS_FILE_NAME = 'settings.json'
PRESETS_DIR = 'presets'
DEFAULT_PRESETS_DIR = 'default_presets'
APP_FRIENDLY_NAME = 'rF2 Settings Widget'
BASE_PATH = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__ + '/..')))
RFACTOR_PLAYER = 'UserData/player/player.JSON'
RFACTOR_DXCONFIG = 'UserData/Config_DX11.ini'

GIT_RELEASE_URL = 'https://api.github.com/repos/tappi287/rf2_video_settings/releases/latest'

UPDATE_VERSION_FILE = 'version.txt'
UPDATE_INSTALL_FILE = 'rF2_Settings_Wizard_{version}_win64.exe'

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


def get_user_presets_dir() -> Path:
    docs_dir = Path(os.path.expanduser('~\\Documents\\' + SETTINGS_DIR_NAME))
    return Path(check_and_create_dir(docs_dir))


def get_user_export_dir() -> Path:
    exp_dir = Path(os.path.expanduser('~\\Documents\\' + SETTINGS_DIR_NAME)) / EXPORT_DIR_NAME
    return Path(check_and_create_dir(exp_dir))


def get_default_presets_dir() -> Path:
    return Path(get_current_modules_dir()) / DEFAULT_PRESETS_DIR


def get_log_dir() -> str:
    log_dir = user_log_dir(SETTINGS_DIR_NAME, '')
    setting_dir = os.path.abspath(os.path.join(log_dir, '../'))
    # Create <app-name>
    check_and_create_dir(setting_dir)
    # Create <app-name>/log
    return check_and_create_dir(log_dir)


def get_version() -> str:
    f = Path('.') / 'vue' / 'package.json'
    if f.is_file():
        try:
            with open(f.as_posix(), 'r') as f:
                pkg = json.load(f)
                return pkg.get('version')
        except Exception as e:
            print('Duh!', e)

    f = Path('.') / 'version.txt'
    try:
        with open(f.as_posix(), 'r') as f:
            version = f.read()
            return version
    except Exception as e:
        print('Duh!', e)

    return '0.0.0'
