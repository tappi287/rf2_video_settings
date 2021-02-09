import json
import logging
from pathlib import WindowsPath
from subprocess import Popen
from typing import Optional

import eel

from ..app_settings import AppSettings
from ..preset import load_presets_from_dir, PRESET_TYPES
from ..presets_dir import get_user_presets_dir, get_user_export_dir
from ..rfactor import RfactorPlayer


def expose_preset_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def get_presets(preset_type: Optional[int] = 0):
    current_preset = PRESET_TYPES.get(preset_type)()

    # - Read the actual, current rFactor Settings
    rf = RfactorPlayer()
    if rf.is_valid:
        current_preset.update(rf)
    else:
        msg = 'Could not detect a rFactor 2 Steam installation with a player.JSON and/or Config_DX11.ini\n'
        msg += rf.error
        logging.fatal(msg)
        return json.dumps({'result': False, 'msg': msg})

    if not AppSettings.create_backup(rf):
        msg = 'Could not find or create backup files!'
        logging.fatal(msg)
        return json.dumps({'result': False, 'msg': msg})

    # - Load saved Presets
    preset_changed = None
    selected_preset_name = AppSettings.selected_preset or current_preset.name

    presets, selected_preset = load_presets_from_dir(get_user_presets_dir(), preset_type,
                                                     current_preset, selected_preset_name)
    presets = [current_preset] + presets

    # - Check if the currently selected preset differs
    #   from the actual rFactor 2 settings on disk.
    #   If they deviate, point the user to the current settings.
    if selected_preset and selected_preset != current_preset:
        preset_changed = selected_preset.name
        logging.debug('Resetting selected Preset to "Current Preset" from %s because settings differ '
                      'from actual rFactor 2 settings.', preset_changed)
        AppSettings.selected_preset = current_preset.name
        selected_preset_name = current_preset.name
        AppSettings.save()

    presets = sorted(presets, key=lambda k: k.name)

    return json.dumps({'result': True, 'presets': [p.to_js() for p in presets],
                       'selected_preset': selected_preset_name,
                       'preset_changed': preset_changed})


@eel.expose
def select_preset(preset_name):
    logging.debug('Updating AppSettings: selected_preset = %s', preset_name)
    AppSettings.selected_preset = preset_name
    AppSettings.save()


@eel.expose
def save_preset(preset_js_dict):
    """ Save the preset to file and update rFactor Settings """
    p = _create_preset_instance_from_js_dict(preset_js_dict)

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
    """ Export a preset to file """
    p = _create_preset_instance_from_js_dict(preset_js_dict)

    if not p.save_unique_file():
        return json.dumps({'result': False, 'msg': f'Error exporting Preset: {p.name}'})

    # -- Open Explorer Window
    export_path = str(WindowsPath(get_user_export_dir()))
    Popen(['explorer', f'/n,{export_path}'])

    return json.dumps({'result': True, 'msg': f'Preset {p.name} exported.'})


@eel.expose
def import_preset(preset_js_dict):
    p = _create_preset_instance_from_js_dict(preset_js_dict)
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


def _create_preset_instance_from_js_dict(preset_js_dict: dict):
    # -- Get preset type and create an instance of it, fallback to GraphicsPreset
    p = PRESET_TYPES.get(preset_js_dict.get('preset_type', 0))()

    # -- Read options from js_dict
    p.from_js_dict(preset_js_dict)

    return p
