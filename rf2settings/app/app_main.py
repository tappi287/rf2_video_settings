import logging
from typing import Optional

import eel
import gevent.event

from rf2settings.app import app_main_fn
from rf2settings.app_settings import AppSettings
from rf2settings.runasadmin import run_as_admin
from rf2settings.utils import AppExceptionHook

CLOSE_EVENT = gevent.event.Event()


def close_callback(page, sockets):
    logging.info('Received eel close callback. Shutting down application. %s %s', page, sockets)
    CLOSE_EVENT.set()


def request_close():
    logging.info('Received close request.')
    CLOSE_EVENT.set()
    if hasattr(eel, 'closeApp'):
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
    return app_main_fn.overwrite_rf_location(value)


@eel.expose
def rf_is_valid():
    return app_main_fn.rf_is_valid()


@eel.expose
def restore_backup():
    return app_main_fn.restore_backup()


@eel.expose
def get_last_launch_method():
    return app_main_fn.get_last_launch_method()


@eel.expose
def run_rfactor(server_info: Optional[dict] = None, method: Optional[int] = 0):
    return app_main_fn.run_rfactor(server_info, method)


@eel.expose
def run_steamvr():
    return app_main_fn.run_steamvr()


@eel.expose
def get_rf_version():
    return app_main_fn.get_rf_version()


@eel.expose
def open_setup_folder():
    return app_main_fn.open_setup_folder()


@eel.expose
def run_mod_mgr():
    return app_main_fn.run_mod_mgr()


@eel.expose
def test_app_exception():
    AppExceptionHook.produce_exception = True


@eel.expose
def get_log():
    return app_main_fn.get_log()


@eel.expose
def open_log_folder():
    return app_main_fn.open_log_folder()


@eel.expose
def set_apply_webui_settings(setting: bool):
    return app_main_fn.set_apply_webui_settings(setting)


@eel.expose
def get_apply_webui_settings():
    return app_main_fn.get_apply_webui_settings()


@eel.expose
def save_app_preferences(app_preferences):
    return app_main_fn.save_app_preferences(app_preferences)


@eel.expose
def load_app_preferences():
    return app_main_fn.load_app_preferences()


def expose_main_methods():
    """ empty method we import to have the exposed methods registered """
    pass
