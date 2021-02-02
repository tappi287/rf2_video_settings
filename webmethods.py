import json
import logging
import sys
from pathlib import WindowsPath
from subprocess import Popen
from typing import Optional

import eel

from rf2settings.app_settings import AppSettings
from rf2settings.presets_dir import get_user_presets_dir, get_user_export_dir
from rf2settings.preset import Preset, load_presets_from_dir
from rf2settings.runasadmin import run_as_admin
from rf2settings.rfactor import RfactorPlayer
from rf2settings.serverlist import ServerList

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)


def expose_methods():
    """ empty method we import to have the exposed methods registered """
    pass


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


"""
Remove auto-updates for now
@eel.expose
def check_for_updates():
    # Report to FrontEnd if a new version is available
    up = GitHubUpdater()
    if up.is_current_version():
        return json.dumps({'result': False, 'version': up.version})

    return json.dumps({'result': True, 'version': up.git_version})


@eel.expose
def download_update():
    # Download the updated setup
    up = GitHubUpdater()
    if not up.is_current_version():
        return json.dumps({'result': up.download_update()})
    return json.dumps({'result': False})


@eel.expose
def run_update():
    # Close the App and run the updated setup
    if GitHubUpdater.execute_update_setup():
        request_close()
        return json.dumps({'result': True})
    return json.dumps({'result': False})
"""


@eel.expose
def get_rf_version():
    rf = RfactorPlayer(only_version=True)
    return json.dumps(rf.version)


@eel.expose
def get_presets():
    current_preset = Preset()

    # - Read the actual, current rFactor Settings
    rf = RfactorPlayer()
    if rf.is_valid:
        current_preset.update(rf)

    if not AppSettings.create_backup(rf):
        logging.fatal('Could not find or create backup files!')
        return

    # - Load saved Presets
    preset_changed = None

    presets, selected_preset = load_presets_from_dir(get_user_presets_dir(), current_preset, AppSettings.selected_preset)
    presets = [current_preset] + presets

    # - Check if the currently selected preset differs
    #   from the actual rFactor 2 settings on disk.
    #   If they deviate, point the user to the current settings.
    if selected_preset and selected_preset != current_preset:
        preset_changed = selected_preset.name
        logging.debug('Resetting selected Preset to "Current Preset" from %s because settings differ '
                      'from actual rFactor 2 settings.', preset_changed)
        AppSettings.selected_preset = current_preset.name
        AppSettings.save()

    presets = sorted(presets, key=lambda k: k.name)
    current_preset.export()

    return json.dumps({'presets': [p.to_js() for p in presets],
                       'selected_preset': AppSettings.selected_preset,
                       'preset_changed': preset_changed})


@eel.expose
def select_preset(preset_name):
    logging.debug('Updating AppSettings: selected_preset = %s', preset_name)
    AppSettings.selected_preset = preset_name
    AppSettings.save()


@eel.expose
def save_preset(preset_js_dict):
    # -- Save the preset
    p = Preset()
    p.from_js_dict(preset_js_dict)
    if not p.save():
        return json.dumps({'result': False, 'msg': f'Error saving Preset: {p.name}'})
    logging.debug('Saved Preset: %s', p.name)

    rf = RfactorPlayer()
    if rf.is_valid:
        if not rf.write_settings(p):
            return json.dumps({'result': False, 'msg': rf.error})
    return json.dumps({'result': True, 'msg': 'Preset saved and rFactor 2 Settings successfully written.'})


@eel.expose
def export_preset(preset_js_dict):
    # -- Export the preset
    p = Preset()
    p.from_js_dict(preset_js_dict)
    if not p.save_unique_file():
        return json.dumps({'result': False, 'msg': f'Error exporting Preset: {p.name}'})

    # -- Open Explorer Window
    export_path = str(WindowsPath(get_user_export_dir()))
    Popen(['explorer', f'/n,{export_path}'])

    return json.dumps({'result': True, 'msg': f'Preset {p.name} exported.'})


@eel.expose
def import_preset(preset_js_dict):
    p = Preset()
    p.from_js_dict(preset_js_dict)
    return json.dumps({'result': True, 'preset': p.to_js()})


@eel.expose
def delete_preset(preset_name):
    default_presets = [f.stem for f in AppSettings.iterate_default_presets()]

    for preset_file in get_user_presets_dir().glob('*.json'):
        if preset_file.stem == preset_name:
            if preset_name in default_presets:
                AppSettings.deleted_defaults.append(preset_name)
            preset_file.unlink()
            logging.debug('Deleted Preset: %s', preset_name)


@eel.expose
def set_user_presets_dir(user_preset_dir):
    return json.dumps({'result': AppSettings.update_user_presets_dir(user_preset_dir)})


@eel.expose
def get_user_presets_dir_web():
    user_presets_dir = str(WindowsPath(get_user_presets_dir()))
    logging.info('Providing User Presets Dir to FrontEnd: %s', user_presets_dir)
    return user_presets_dir


@eel.expose
def get_server_list():
    server_list = ServerList(update_players=True)
    server_list.update(eel.add_server_list_chunk, eel.server_progress)
    return json.dumps({'result': server_list.servers})


@eel.expose
def refresh_server(address: list):
    server_list = ServerList()

    if len(address) > 1:
        address = (address[0], int(address[1]))
        server_info = server_list.update_single(address)
        if server_info:
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


@eel.expose
def run_rfactor_config():
    rf, result = RfactorPlayer(), False
    if rf.is_valid:
        result = rf.run_config()

    return json.dumps({'result': result})
