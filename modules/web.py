import json
import logging
import random
import sys
from pathlib import WindowsPath
from subprocess import Popen

import eel

from .app_settings import AppSettings
from .globals import get_user_presets_dir
from .preset import Preset, load_presets_from_dir
from .rfactor import RfactorPlayer

# -- Log to Stdout keeping it short
logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)


@eel.expose
def message():
    return f'A random message from Python: {random.random()}'


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
    if not p.export():
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
    presets_path = str(WindowsPath(get_user_presets_dir()))
    Popen(['explorer', f'/n,{presets_path}'])

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