import json

import eel

from rf2settings.rfactor import RfactorPlayer


def expose_dashboard_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def get_rf_settings():
    rf = RfactorPlayer()
    if rf.is_valid:
        return json.dumps({'result': rf.driver_options})
    return json.dumps({'result': False})

