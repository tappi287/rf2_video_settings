import eel

from rf2settings.app import app_opencomposite_fn


@eel.expose
def get_opencomposite_status():
    return app_opencomposite_fn.get_opencomposite_status()


@eel.expose
def download_opencomposite():
    return app_opencomposite_fn.download_opencomposite()


@eel.expose
def enable_opencomposite():
    return app_opencomposite_fn.enable_opencomposite()


@eel.expose
def restore_original_openvr():
    return app_opencomposite_fn.restore_original_openvr()


def expose_opencomposite_methods():
    """ empty method we import to have the exposed methods registered """
    pass
