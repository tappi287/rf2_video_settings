import eel

from . import app_graphics_fn


def expose_graphics_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def get_current_dx_config():
    return app_graphics_fn.get_current_dx_config()


@eel.expose
def run_rfactor_config():
    return app_graphics_fn.run_rfactor_config()
