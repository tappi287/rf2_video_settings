import json
import logging
import subprocess
from pathlib import WindowsPath, Path
from subprocess import Popen
from typing import Optional

from ..app_settings import AppSettings
from ..globals import DEFAULT_PRESET_NAME, RFACTOR_SETUPS, RFACTOR_MODMGR, get_log_file, get_log_dir, get_data_dir
from ..preset.preset import PresetType
from ..preset.preset_base import load_preset
from ..rf2command import CommandQueue, Command
from ..rf2connect import RfactorState
from ..rfactor import RfactorPlayer, RfactorLocation
from ..utils import capture_app_exceptions
from ..valve.steam_utils import SteamApps


def _get_rf_location(sub_path):
    rf = RfactorPlayer(only_version=True)
    rf_path = rf.location / sub_path
    if not rf_path.exists():
        logging.error('Could not locate rF2 Setups directory in %s', rf_path.as_posix())
        return
    return str(WindowsPath(rf_path))


@capture_app_exceptions
def overwrite_rf_location(value):
    def reset_location():
        AppSettings.rf_overwrite_location = ''
        RfactorLocation.overwrite_location(None)

    if Path(value).exists() and Path(value).is_dir() and Path(value) != Path(''):
        AppSettings.rf_overwrite_location = Path(value).as_posix()
        RfactorLocation.overwrite_location(AppSettings.rf_overwrite_location)
        RfactorLocation.get_location()
        if not RfactorLocation.is_valid:
            logging.warning(f'Invalid overwrite location: {value}. Resetting rF2 location.')
            reset_location()
            result = False
        else:
            logging.warning('Overwriting rf2 location: %s', Path(value).as_posix())
            result = True
    else:
        reset_location()
        logging.warning('Overwriting rf2 location cleared!')
        result = True

    AppSettings.save()
    return result


@capture_app_exceptions
def rf_is_valid():
    rf = RfactorPlayer()
    logging.info('Detected valid rF2 installation: %s %s', rf.is_valid, rf.location)
    return json.dumps(rf.is_valid)


@capture_app_exceptions
def restore_backup():
    rf = RfactorPlayer()

    # -- Restore some default settings and remove ReShade etc.
    default_preset_file = get_data_dir() / DEFAULT_PRESET_NAME
    default_preset = load_preset(default_preset_file, PresetType.graphics)
    rf.write_settings(default_preset)

    if not rf.is_valid:
        return json.dumps({'result': False, 'msg': rf.error})

    if AppSettings.restore_backup(rf):
        logging.info('Original settings restored!')
        return json.dumps({'result': True, 'msg': 'BackUp files restored!'})

    return json.dumps({'result': False, 'msg': 'Could not restore all back up files! Make sure you '
                                               'did not deleted any *.original files!'})


@capture_app_exceptions
def get_last_launch_method() -> Optional[int]:
    return AppSettings.last_launch_method


@capture_app_exceptions
def run_rfactor(server_info: Optional[dict] = None, method: Optional[int] = 0):
    logging.info('UI requested rF2 run with method: %s', method)
    if method is None:
        method = AppSettings.last_launch_method
        logging.info('Launching rF2 with last known method: %s', method)

    if server_info and server_info.get('password_remember'):
        # -- Store password if remember option checked
        logging.info('Storing password for Server %s', server_info.get('id'))
        AppSettings.server_passwords[server_info.get('id')] = server_info.get('password')
        AppSettings.save()
    elif server_info and not server_info.get('password_remember'):
        # -- Delete password if remember option unchecked
        if server_info.get('id') in AppSettings.server_passwords:
            AppSettings.server_passwords.pop(server_info.get('id'))
            AppSettings.save()

    AppSettings.last_launch_method = method
    AppSettings.save()

    rf, result = RfactorPlayer(), False
    if rf.is_valid:
        result = rf.run_rfactor(method, server_info)
        if not server_info:
            CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=10.0))

    return json.dumps({'result': result, 'msg': rf.error})


@capture_app_exceptions
def run_steamvr():
    try:
        steam_path = Path(SteamApps.find_steam_location()) / 'steam.exe'
        cmd = [str(WindowsPath(steam_path)), '-applaunch', "250820"]
        subprocess.Popen(cmd)
    except Exception as e:
        return json.dumps({'result': False, 'msg': f'Error launching SteamVR: {e}'})
    return json.dumps({'result': True, 'msg': 'Launched SteamVR'})


@capture_app_exceptions
def get_rf_version():
    rf = RfactorPlayer(only_version=True)
    return json.dumps({'version': rf.version, 'location': str(rf.location)})


@capture_app_exceptions
def open_setup_folder():
    setup_path = _get_rf_location(RFACTOR_SETUPS)
    if setup_path is None:
        return
    logging.info('Opening folder: %s', setup_path)
    Popen(f'explorer /n,"{setup_path}"')


@capture_app_exceptions
def run_mod_mgr():
    mod_mgr_path = _get_rf_location(RFACTOR_MODMGR)
    if mod_mgr_path is None:
        return
    logging.info('Opening ModMgr: %s', mod_mgr_path)
    Popen(mod_mgr_path, cwd=WindowsPath(mod_mgr_path).parent.parent)


@capture_app_exceptions
def get_log():
    log_file_path = get_log_file()
    try:
        with open(log_file_path, 'r') as l:
            return json.dumps({'result': True, 'log': l.read()}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({'result': False, 'msg': str(e)})


@capture_app_exceptions
def open_log_folder():
    log_dir = str(WindowsPath(get_log_dir()))
    logging.info('Opening folder: %s', log_dir)
    Popen(f'explorer /n,"{log_dir}"')
    return json.dumps({'result': True, })


@capture_app_exceptions
def set_apply_webui_settings(setting: bool):
    AppSettings.apply_webui_settings = setting
    AppSettings.save()
    logging.debug('Updated apply_webui_settings: %s', AppSettings.apply_webui_settings)
    return json.dumps({'result': True, })


@capture_app_exceptions
def get_apply_webui_settings():
    logging.debug('Providing Ui with apply_webui_settings: %s', AppSettings.apply_webui_settings)
    return json.dumps({'result': True, 'setting': AppSettings.apply_webui_settings})


@capture_app_exceptions
def save_app_preferences(app_preferences: dict):
    AppSettings.app_preferences = app_preferences
    AppSettings.save()
    return json.dumps({'result': True})


@capture_app_exceptions
def load_app_preferences():
    return json.dumps({'result': True, 'preferences': AppSettings.app_preferences})
