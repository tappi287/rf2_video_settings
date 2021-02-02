import json
import logging
from typing import Optional

import eel

from .app_settings import AppSettings
from .rfactor import RfactorPlayer
from .runasadmin import run_as_admin


def request_close():
    logging.info('Received close request.')
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
def run_rfactor(server_info: Optional[dict] = None):
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
        result = rf.run_rfactor(server_info)

    return json.dumps({'result': result})


def expose_main_methods():
    """ empty method we import to have the exposed methods registered """
    pass