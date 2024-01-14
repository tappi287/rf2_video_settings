import json

from ..preset.preset import GraphicsPreset
from ..rfactor import RfactorPlayer
from ..utils import capture_app_exceptions


@capture_app_exceptions
def get_current_dx_config():
    rf = RfactorPlayer()
    if not rf.is_valid:
        return json.dumps({'result': False})

    rp = GraphicsPreset()
    rp.update(rf)
    return json.dumps({'result': True, 'preset': rp.to_js()})


@capture_app_exceptions
def run_rfactor_config():
    rf, result = RfactorPlayer(), False
    if rf.is_valid:
        result = rf.run_config()

    return json.dumps({'result': result, 'msg': rf.error})
