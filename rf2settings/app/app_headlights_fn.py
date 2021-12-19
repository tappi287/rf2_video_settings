import json
import logging
from typing import Tuple, Optional

from ..app_settings import AppSettings
from ..directInputKeySend import rfKeycodeToDIK, KeycodeToDIK, DirectInputKeyCodeTable
from ..gamecontroller import ControllerEvents
from ..preset.preset import HeadlightControlsSettingsPreset
from ..preset.settings_model import HeadlightSettings, HeadlightControllerAssignments, HeadlightControllerJsonSettings
from ..rfactor import RfactorPlayer
from ..utils import capture_app_exceptions


def read_rfactor_headlight_settings() -> Tuple[
    bool, str, Optional[RfactorPlayer], Optional[HeadlightControlsSettingsPreset]
]:
    # - Read the actual, current rFactor Settings
    current_preset = HeadlightControlsSettingsPreset()
    rf = RfactorPlayer()
    if rf.is_valid:
        current_preset.update(rf)
    else:
        msg = 'An error occurred trying to read settings:\n'
        msg += rf.error
        logging.fatal(msg)
        return False, msg, None, None

    return True, '', rf, current_preset


@capture_app_exceptions
def get_rfactor_key_name(rf_keycode):
    """ Convert an rFactor keycode to a readable letter/name """
    dik_key = rfKeycodeToDIK(int(rf_keycode))
    return json.dumps(dik_key[4:])


@capture_app_exceptions
def get_rfactor_keycode_from_js_keycode(js_keycode):
    """ Convert JS keycode to an rFactor keycode """
    dik_key = KeycodeToDIK(js_keycode)
    return json.dumps(DirectInputKeyCodeTable.get(dik_key, (0, 0))[0])


@capture_app_exceptions
def get_headlights_settings():
    # -- Prepare rFactorPlayer instance and current preset
    result, msg, rf, current_preset = read_rfactor_headlight_settings()
    if not result:
        return json.dumps({'result': False, 'msg': msg})

    try:
        headlight_settings = HeadlightSettings()
        headlight_settings.from_js_dict(AppSettings.headlight_settings)

        controller_assignments = HeadlightControllerAssignments()
        controller_assignments.from_js_dict(AppSettings.headlight_controller_assignments)

        rf_controller_map = getattr(current_preset, HeadlightControllerJsonSettings.app_key)
    except Exception as e:
        logging.error('Could not load headlight settings: %s', e)
        return json.dumps({'result': False, 'msg': str(e)})

    logging.debug('Headlight settings loaded!')
    return json.dumps({'result': True,
                       headlight_settings.app_key: headlight_settings.to_js(),
                       controller_assignments.app_key: controller_assignments.to_js_object(),
                       rf_controller_map.app_key: rf_controller_map.to_js()
                       }
                      )


@capture_app_exceptions
def save_headlights_settings(settings: dict):
    # -- Prepare rFactorPlayer instance and current preset
    result, msg, rf, current_preset = read_rfactor_headlight_settings()
    if not result:
        return json.dumps({'result': False, 'msg': msg})

    try:
        # -- Update Headlight App Settings
        headlight_settings = HeadlightSettings()
        headlight_settings.from_js_dict(settings.get(headlight_settings.app_key))
        AppSettings.headlight_settings = headlight_settings.to_js()

        # -- Update Controller Mappings
        controller_assignments = HeadlightControllerAssignments()
        controller_assignments.from_js_dict(settings.get(controller_assignments.app_key))
        AppSettings.headlight_controller_assignments = controller_assignments.to_js_object()

        # -- Update Current rFactor Preset
        rf_controller_options = HeadlightControllerJsonSettings()
        rf_controller_options.from_js_dict(settings.get(HeadlightControllerJsonSettings.app_key))
        setattr(current_preset, rf_controller_options.app_key, rf_controller_options)
        # -- Write updated rFactor settings
        if not rf.write_settings(current_preset):
            logging.error('Error writing rFactor 2 settings: %s', rf.error)
            return json.dumps({'result': False, 'msg': rf.error})

        # -- Get rFactor Headlight DIK keycode
        rf_opt = rf_controller_options.get_option('Control - Headlights')
        if rf_opt:
            if isinstance(rf_opt.value, list) and len(rf_opt.value) > 1:
                rf_keycode = rf_opt.value[1]
                AppSettings.headlight_rf_key = rfKeycodeToDIK(rf_keycode)

        # -- Save settings
        AppSettings.save()
    except Exception as e:
        logging.error('Could not save headlight settings: %s', e)
        return json.dumps({'result': False, 'msg': str(e)})

    # -- Signal a settings change
    ControllerEvents.settings_changed.set()

    logging.debug('Saved headlight settings!')
    return json.dumps({'result': True})
