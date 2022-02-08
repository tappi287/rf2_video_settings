import json
import logging
from pathlib import WindowsPath
from subprocess import Popen

import gevent

from ..app_settings import AppSettings
from ..preset.preset import PresetType
from ..preset.preset_base import PRESET_TYPES, load_presets_from_dir
from ..preset.presets_dir import get_user_presets_dir, get_user_export_dir
from ..preset.settings_model import VideoSettings
from ..rf2events import RfactorStatusEvent
from ..rfactor import RfactorPlayer
from ..utils import create_file_safe_name, capture_app_exceptions


@capture_app_exceptions
def get_presets(preset_type: int):
    current_preset = PRESET_TYPES.get(preset_type)()

    # - Read the actual, current rFactor Settings
    rf = RfactorPlayer()
    if rf.is_valid:
        current_preset.update(rf)
    else:
        msg = 'An error occurred trying to read settings:\n'
        msg += rf.error
        logging.fatal(msg)
        return json.dumps({'result': False, 'msg': msg})

    if not AppSettings.create_backup(rf):
        msg = 'Could not find or create backup files!'
        logging.fatal(msg)
        return json.dumps({'result': False, 'msg': msg})

    # - Load saved Presets
    preset_changed = None
    selected_preset_name = AppSettings.selected_presets.get(str(preset_type)) or current_preset.name

    presets, selected_preset = load_presets_from_dir(get_user_presets_dir(), preset_type,
                                                     current_preset, selected_preset_name)
    if selected_preset:
        logging.info('Selected Preset %s for type %s', selected_preset.name, selected_preset.__class__.__name__)

    # - Check if the currently selected preset differs
    #   from the actual rFactor 2 settings on disk.
    #   If they deviate, point the user to the current settings.
    if selected_preset and selected_preset != current_preset:
        preset_changed = selected_preset.name
        logging.debug('Resetting selected Preset to "Current Preset" from %s because settings differ '
                      'from actual rFactor 2 settings.', preset_changed)
        AppSettings.selected_presets[str(preset_type)] = current_preset.name
        selected_preset_name = current_preset.name
        AppSettings.save()

    presets = sorted(presets, key=lambda k: k.name)
    presets = [current_preset] + presets

    # -- Remove obsolete settings
    if preset_type == PresetType.graphics and rf.version >= '1.1123':
        for p in presets:
            if not hasattr(p, VideoSettings.app_key):
                continue
            video_settings: VideoSettings = getattr(p, VideoSettings.app_key)
            for o in video_settings.options:
                if o.key == 'FSAA':
                    video_settings.options.remove(o)
                    break

    return json.dumps({'result': True, 'presets': [p.to_js() for p in presets],
                       'selected_preset': selected_preset_name,
                       'preset_changed': preset_changed})


@capture_app_exceptions
def select_preset(preset_name: str, preset_type: int):
    logging.debug('Updating AppSettings: selected_preset = %s %s', preset_name, preset_type)

    AppSettings.selected_presets[str(preset_type)] = preset_name
    AppSettings.save()


@capture_app_exceptions
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

    # -- Update WebUi Session Settings for next run
    AppSettings.update_webui_settings(rf)

    return json.dumps({'result': True, 'msg': 'Preset saved and rFactor 2 Settings successfully written.'})


@capture_app_exceptions
def export_preset(preset_js_dict):
    """ Export a preset to file """
    p = _create_preset_instance_from_js_dict(preset_js_dict)

    if not p.save_unique_file():
        return json.dumps({'result': False, 'msg': f'Error exporting Preset: {p.name}'})

    # -- Open Explorer Window
    export_path = str(WindowsPath(get_user_export_dir()))
    Popen(f'explorer /n,"{export_path}"')

    return json.dumps({'result': True, 'msg': f'Preset {p.name} exported.'})


@capture_app_exceptions
def import_preset(preset_js_dict):
    p = _create_preset_instance_from_js_dict(preset_js_dict)

    # -- Save imported preset
    if not p.save():
        return json.dumps({'result': False, 'msg': f'Error saving imported Preset: {p.name} to disk!'})
    logging.debug('Saved imported Preset: %s', p.name)

    return json.dumps({'result': True, 'preset': p.to_js()})


@capture_app_exceptions
def import_player_json(player_json_dict, preset_type: int):
    # -- Feed Rfactor Player instance with player.JSON dict
    rf = RfactorPlayer(player_json_dict)
    if not rf.is_valid:
        return json.dumps({'result': False, 'msg': rf.error})

    # -- Get preset type and create an instance of it, fallback to GraphicsPreset
    p = PRESET_TYPES.get(preset_type or 0)(desc='Preset imported from a player.JSON file')
    p.update(rf, preset_name='Import')
    p.name = p.find_unique_preset_name()

    # -- Save imported preset
    if not p.save():
        return json.dumps({'result': False, 'msg': f'Error saving imported Preset: {p.name} to disk!'})
    logging.debug('Saved imported Preset: %s', p.name)

    return json.dumps({'result': True, 'preset': p.to_js(),
                       'msg': f'Imported {p.__class__.__name__} data from player.json to {p.name}'})


@capture_app_exceptions
def delete_preset(preset_name, preset_type):
    type_prefix = PRESET_TYPES.get(int(preset_type))().prefix
    preset_name = create_file_safe_name(f'{type_prefix}_{preset_name}')
    default_presets = [f.stem for f in AppSettings.iterate_default_presets()]

    for preset_file in get_user_presets_dir().glob('*.json'):
        if preset_file.stem == preset_name:
            if preset_name in default_presets:
                AppSettings.deleted_defaults.append(preset_name)
            preset_file.unlink()
            logging.debug('Deleted Preset: %s', preset_name)
            return json.dumps({'result': True})

    logging.error('Could not delete Preset: %s', preset_name)
    return json.dumps({'result': False})


@capture_app_exceptions
def set_user_presets_dir(user_preset_dir):
    return json.dumps({'result': AppSettings.update_user_presets_dir(user_preset_dir)})


@capture_app_exceptions
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


@capture_app_exceptions
def restore_pre_replay_preset():
    if AppSettings.replay_playing:
        if AppSettings.replay_preset != '':
            # -- Get currently selected graphics preset
            selected_preset_name = AppSettings.selected_presets.get(str(PresetType.graphics))
            _, selected_preset = load_presets_from_dir(get_user_presets_dir(), PresetType.graphics,
                                                       selected_preset_name=selected_preset_name)
            if not selected_preset:
                return

            RfactorStatusEvent.set(f'Applying pre-replay graphics preset: {selected_preset.name}')
            gevent.sleep(1.0)  # If rf2 just quit, give it some time to write settings

            # -- Apply selected preset to rF2
            if selected_preset:
                rf = RfactorPlayer()
                if rf.is_valid:
                    logging.info('Restoring non-replay preset %s', selected_preset_name)
                    rf.write_settings(selected_preset)
        AppSettings.replay_playing = False
        AppSettings.save()
