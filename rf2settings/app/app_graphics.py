import json

import eel

from rf2settings.rfactor import RfactorPlayer


def expose_graphics_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def run_rfactor_config():
    rf, result = RfactorPlayer(), False
    if rf.is_valid:
        result = rf.run_config()

    return json.dumps({'result': result})
