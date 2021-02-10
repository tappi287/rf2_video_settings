import json

import eel

from rf2settings.preset.preset import GraphicsPreset
from rf2settings.rfactor import RfactorPlayer


def expose_graphics_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def get_current_dx_config():
    rf = RfactorPlayer()
    if not rf.is_valid:
        return json.dumps({'result': False})

    rp = GraphicsPreset()
    rp.update(rf)
    return json.dumps({'result': True, 'preset': rp.to_js()})


@eel.expose
def run_rfactor_config():
    rf, result = RfactorPlayer(), False
    if rf.is_valid:
        result = rf.run_config()

    return json.dumps({'result': result, 'msg': rf.error})
