import eel

from . import app_content_fn


def expose_content_methods():
    pass


@eel.expose
def get_content():
    return app_content_fn.get_content()


@eel.expose
def refresh_content():
    return app_content_fn.refresh_content()
