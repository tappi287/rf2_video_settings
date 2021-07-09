import json
import logging
from pathlib import WindowsPath, Path
from subprocess import Popen
from typing import Optional

import eel
import gevent.event

from rf2settings.app_settings import AppSettings
from rf2settings.globals import RFACTOR_SETUPS, RFACTOR_MODMGR, get_log_file, get_log_dir
from rf2settings.rf2command import CommandQueue, Command
from rf2settings.rf2connect import RfactorState
from rf2settings.rfactor import RfactorPlayer, RfactorLocation
from rf2settings.runasadmin import run_as_admin
from rf2settings.utils import AppExceptionHook

CLOSE_EVENT = gevent.event.Event()


def request_close():
    logging.info('Received close request.')
    CLOSE_EVENT.set()
    eel.closeApp()(close_js_result)


def close_js_result(result):
    logging.info('JS close app result: %s', result)


@eel.expose
def close_request():
    request_close()


@eel.expose
def re_run_admin():
    AppSettings.needs_admin = True
    AppSettings.save()

    if not run_as_admin():
        request_close()


@eel.expose
def reset_admin():
    AppSettings.needs_admin = False
    AppSettings.save()

    request_close()


@eel.expose
def overwrite_rf_location(value):
    result = False
    if Path(value).exists() and Path(value).is_dir() and Path(value) != Path('.'):
        AppSettings.rf_overwrite_location = Path(value).as_posix()
        RfactorLocation.overwrite_location(AppSettings.rf_overwrite_location)
        logging.warning('Overwriting rf2 location: %s', Path(value).as_posix())
        result = True
    else:
        logging.warning('Overwriting rf2 location cleared!')
        AppSettings.rf_overwrite_location = ''
        RfactorLocation.overwrite_location(None)

    AppSettings.save()
    return result


@eel.expose
def rf_is_valid():
    rf = RfactorPlayer()
    logging.info('Detected valid rF2 installation: %s %s', rf.is_valid, rf.location)
    return json.dumps(rf.is_valid)


@eel.expose
def restore_backup():
    rf = RfactorPlayer()

    if not rf.is_valid:
        return json.dumps({'result': False, 'msg': rf.error})

    if AppSettings.restore_backup(rf):
        logging.info('Original settings restored!')
        return json.dumps({'result': True, 'msg': 'BackUp files restored!'})

    return json.dumps({'result': False, 'msg': 'Could not restore all back up files! Make sure you '
                                               'did not deleted any *.original files!'})


@eel.expose
def run_rfactor(server_info: Optional[dict] = None, method: Optional[int] = 0):
    logging.info('UI requested rF2 run with method: %s', method)
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

    rf, result = RfactorPlayer(), False
    if rf.is_valid:
        result = rf.run_rfactor(method, server_info)
        if not server_info:
            CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=10.0))

    return json.dumps({'result': result, 'msg': rf.error})


def _get_rf_location(sub_path):
    rf = RfactorPlayer(only_version=True)
    rf_path = rf.location / sub_path
    if not rf_path.exists():
        logging.error('Could not locate rF2 Setups directory in %s', rf_path.as_posix())
        return
    return str(WindowsPath(rf_path))


@eel.expose
def get_rf_version():
    rf = RfactorPlayer(only_version=True)
    return json.dumps({'version': rf.version, 'location': str(rf.location)})


@eel.expose
def open_setup_folder():
    setup_path = _get_rf_location(RFACTOR_SETUPS)
    if setup_path is None:
        return
    logging.info('Opening folder: %s', setup_path)
    Popen(f'explorer /n,"{setup_path}"')


@eel.expose
def run_mod_mgr():
    mod_mgr_path = _get_rf_location(RFACTOR_MODMGR)
    if mod_mgr_path is None:
        return
    logging.info('Opening ModMgr: %s', mod_mgr_path)
    Popen(mod_mgr_path, cwd=WindowsPath(mod_mgr_path).parent.parent)


@eel.expose
def test_app_exception():
    AppExceptionHook.produce_exception = True


@eel.expose
def get_log():
    log_file_path = get_log_file()
    try:
        with open(log_file_path, 'r') as l:
            return json.dumps({'result': True, 'log': l.read()}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({'result': False, 'msg': str(e)})


@eel.expose
def open_log_folder():
    log_dir = str(WindowsPath(get_log_dir()))
    logging.info('Opening folder: %s', log_dir)
    Popen(f'explorer /n,"{log_dir}"')
    return json.dumps({'result': True, })


@eel.expose
def set_apply_webui_settings(setting: bool):
    AppSettings.apply_webui_settings = setting
    AppSettings.save()
    logging.debug('Updated apply_webui_settings: %s', AppSettings.apply_webui_settings)
    return json.dumps({'result': True, })


@eel.expose
def get_apply_webui_settings():
    logging.debug('Providing Ui with apply_webui_settings: %s', AppSettings.apply_webui_settings)
    return json.dumps({'result': True, 'setting': AppSettings.apply_webui_settings})


def expose_main_methods():
    """ empty method we import to have the exposed methods registered """
    pass
