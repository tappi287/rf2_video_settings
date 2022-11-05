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


@eel.expose
def get_device_list():
    return app_controller_fn.get_device_list()


@eel.expose
def save_device_list(js_device_list):
    return app_controller_fn.save_device_list(js_device_list)


@eel.expose
def remove_from_device_list(device_guid):
    return app_controller_fn.remove_from_device_list(device_guid)
