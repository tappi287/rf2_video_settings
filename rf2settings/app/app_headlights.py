import json
import logging

import eel

from ..app_settings import AppSettings
from ..preset.settings_model import HeadlightSettings, HeadlightControllerAssignments


def expose_headlights_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def get_headlights_settings():
    try:
        headlight_settings = HeadlightSettings()
        headlight_settings.from_js_dict(AppSettings.headlight_settings)

        controller_assignments = HeadlightControllerAssignments()
        controller_assignments.from_js_dict(AppSettings.headlight_controller_assignments)
    except Exception as e:
        logging.error('Could not load headlight settings: %s', e)
        return json.dumps({'result': False, 'msg': str(e)})

    logging.debug('Headlight settings loaded!')
    return json.dumps({'result': True,
                       headlight_settings.app_key: headlight_settings.to_js(),
                       controller_assignments.app_key: controller_assignments.to_js_object()}
                      )


@eel.expose
def save_headlights_settings(settings: dict):
    try:
        headlight_settings = HeadlightSettings()
        headlight_settings.from_js_dict(settings.get(headlight_settings.app_key))
        AppSettings.headlight_settings = headlight_settings.to_js()

        controller_assignments = HeadlightControllerAssignments()
        controller_assignments.from_js_dict(settings.get(controller_assignments.app_key))
        AppSettings.headlight_controller_assignments = controller_assignments.to_js_object()

        AppSettings.save()
    except Exception as e:
        logging.error('Could not save headlight settings: %s', e)
        return json.dumps({'result': False, 'msg': str(e)})

    logging.debug('Saved headlight settings!')
    return json.dumps({'result': True})
