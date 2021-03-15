import json
import logging

import eel

from rf2settings.app_settings import AppSettings
from rf2settings.rfactor import RfactorPlayer
from rf2settings.serverlist import ServerList


def expose_multiplayer_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def get_rf_version():
    rf = RfactorPlayer(only_version=True)
    return json.dumps(rf.version)


@eel.expose
def get_server_list(only_favourites: bool = False):
    server_list = ServerList(update_players=True, only_favourites=only_favourites)
    server_list.update(eel.add_server_list_chunk, eel.server_progress)
    return json.dumps({'result': server_list.servers})


@eel.expose
def refresh_server(address: list):
    server_list = ServerList()

    if len(address) > 1:
        address = (address[0], int(address[1]))
        server_info = server_list.update_single(address)
        if server_info:
            logging.debug('Updated Server info for: %s', server_info.get('server_name'))
            return json.dumps({'result': server_info, 'msg': f'Server info updated for {address[0]}'})

    return json.dumps({'result': False, 'msg': 'Could not obtain server info for this address'})


@eel.expose
def get_server_browser_settings():
    return json.dumps(AppSettings.server_browser)


@eel.expose
def save_server_browser_settings(server_browser: dict):
    AppSettings.server_browser.update(server_browser)
    if AppSettings.save():
        logging.debug('Updated Server Browser settings.')
        return json.dumps({'result': True})
    return json.dumps({'result': False})


@eel.expose
def get_server_favourites():
    return json.dumps(AppSettings.server_favourites)


@eel.expose
def server_favourite(server_info, add: bool = True):
    if not server_info.get('id'):
        return json.dumps({'result': False})

    # -- Add favourite
    if add:
        logging.debug('Adding Server favourite = %s %s', server_info.get('id'), add)
        if server_info.get('id') not in AppSettings.server_favourites:
            AppSettings.server_favourites.append(server_info.get('id'))
        AppSettings.save()
        return json.dumps({'result': True, 'data': AppSettings.server_favourites})

    # -- Remove favourite
    if server_info.get('id') in AppSettings.server_favourites:
        logging.debug('Removing Server favourite = %s %s', server_info.get('id'), add)
        AppSettings.server_favourites.remove(server_info.get('id'))
        AppSettings.save()

    return json.dumps({'result': True, 'data': AppSettings.server_favourites})