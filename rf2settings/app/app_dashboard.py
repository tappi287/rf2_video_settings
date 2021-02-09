import json

import eel

from rf2settings.rfactor import RfactorPlayer


def expose_dashboard_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def get_rf_driver():
    rf = RfactorPlayer()
    if rf.is_valid:
        return json.dumps({'result': rf.options.driver_options.to_js()})

    return json.dumps({'result': False, 'msg': rf.error})
