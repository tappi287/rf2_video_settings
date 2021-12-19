import eel

from . import app_headlights_fn


def expose_headlights_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def get_rfactor_key_name(rf_keycode):
    """ Convert an rFactor keycode to a readable letter/name """
    return app_headlights_fn.get_rfactor_key_name(rf_keycode)


@eel.expose
def get_rfactor_keycode_from_js_keycode(js_keycode):
    return app_headlights_fn.get_rfactor_keycode_from_js_keycode(js_keycode)


@eel.expose
def get_headlights_settings():
    return app_headlights_fn.get_headlights_settings()


@eel.expose
def save_headlights_settings(settings: dict):
    return app_headlights_fn.save_headlights_settings(settings)
