import os
import logging
import sys
import json
from pathlib import Path
from typing import Union

from appdirs import user_data_dir, user_log_dir

from .knownpaths import get_current_user_documents_path


APP_NAME = 'rf2_settings_widget'
SETTINGS_DIR_NAME = 'rf2_settings_widget'
EXPORT_DIR_NAME = 'exported'
PRESETS_DIR = 'presets'
DEFAULT_PRESETS_DIR = 'default_presets'
DATA_DIR = 'data'
RESHADE_ZIP = 'VRToolkitReshadeUniversal_0.9.4-pre.zip'
RESHADE_PRESET_SRC = 'ReShade/rf2_settings_widget_presets/'
RESHADE_PRESET_DIR = 'ReShade/Presets/'
RESHADE_TARGET_PRESET_NAME = 'generic_vr.ini'
RESHADE_LEGACY = ('ReShadePreset.ini', 'ReShadePreset_Instagram.ini', 'ReShadePreset_Sharpen.ini', 'reshade-shaders')
APP_FRIENDLY_NAME = 'rF2 Settings Widget'
BASE_PATH = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__ + '/..')))
RFACTOR_PLAYER = 'UserData/player/player.JSON'
RFACTOR_CONTROLLER = 'UserData/player/Controller.JSON'
RFACTOR_DXCONFIG = 'UserData/Config_DX11.ini'
RFACTOR_VERSION_TXT = 'Core/Version.txt'
RFACTOR_SETUPS = 'UserData/player/Settings'
RFACTOR_LOG = 'UserData/Log'
RFACTOR_MODMGR = 'Bin64/ModMgr.exe'

GIT_RELEASE_URL = 'https://api.github.com/repos/tappi287/rf2_video_settings/releases/latest'

UPDATE_VERSION_FILE = 'version.txt'
UPDATE_INSTALL_FILE = 'rF2_Settings_Wizard_{version}_win64.exe'

DEFAULT_LOG_LEVEL = 'DEBUG'

KNOWN_APPS = {
    "365960": {
        "name": "rFactor 2",
        "installdir": "rFactor 2",
        "executable": "rFactor2.exe",
        "exe_sub_path": "Bin64/"
    },
    "908520": {
        "name": "fpsVR",
        "installdir": "fpsVR",
        "executable": "fpsVR.exe",
        "exe_sub_path": ""
    }
}

RF2_APPID = [k for k in KNOWN_APPS.keys()][0]

# Frozen or Debugger
if getattr(sys, 'frozen', False):
    # -- Running in PyInstaller Bundle ---
    FROZEN = True
else:
    # -- Running in IDE ---
    FROZEN = False

SETTINGS_FILE_NAME = 'settings.json' if FROZEN else 'settings_dev.json'
SETTINGS_CONTENT_FILE_NAME = 'content.json'


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


def get_present_mon_bin() -> Path:
    bin_dir = Path(get_current_modules_dir()) / 'bin'
    present_mon_exe = bin_dir / 'PresentMon-1.7.0-x64.exe'

    for f in bin_dir.glob('PresentMon*.exe'):
        if f:
            present_mon_exe = f
            break

    return present_mon_exe


def _get_user_doc_dir() -> Path:
    docs_dir = get_current_user_documents_path()
    if not docs_dir:
        docs_dir = os.path.expanduser('~\\Documents\\')
    return Path(docs_dir)


def get_default_presets_dir() -> Path:
    if FROZEN:
        return Path(get_current_modules_dir()) / DEFAULT_PRESETS_DIR
    else:
        return Path(get_current_modules_dir()) / 'rf2settings' / DEFAULT_PRESETS_DIR


def get_data_dir() -> Path:
    return Path(get_current_modules_dir()) / DATA_DIR


def get_log_dir() -> str:
    log_dir = user_log_dir(SETTINGS_DIR_NAME, '')
    setting_dir = os.path.abspath(os.path.join(log_dir, '../'))
    # Create <app-name>
    check_and_create_dir(setting_dir)
    # Create <app-name>/log
    return check_and_create_dir(log_dir)


def get_log_file() -> Path:
    if FROZEN:
        return Path(get_log_dir()) / f'{APP_NAME}.log'
    else:
        return Path(get_log_dir()) / f'{APP_NAME}_DEV.log'


def get_version() -> str:
    f = Path('.') / 'vue' / 'package.json'
    if f.is_file():
        try:
            with open(f.as_posix(), 'r') as f:
                pkg = json.load(f)
                return pkg.get('version')
        except Exception as e:
            print('Duh!', e)

    f = Path('../modules') / 'version.txt'
    try:
        with open(f.as_posix(), 'r') as f:
            version = f.read()
            return version
    except Exception as e:
        print('Duh!', e)

    return '0.0.0'


def find_subclasses(module, clazz):
    for name in dir(module):
        o = getattr(module, name)
        try:
            if (o != clazz) and issubclass(o, clazz):
                yield name, o
        except TypeError:
            pass
