import eel

from . import app_controller_fn


def expose_controller_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def start_controller_capture():
    return app_controller_fn.start_controller_capture()


@eel.expose
def stop_controller_capture():
    return app_controller_fn.stop_controller_capture()
