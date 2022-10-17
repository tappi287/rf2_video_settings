import eel

from . import app_chat_fn


def expose_chat_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def save_chat_settings(settings):
    return app_chat_fn.save_chat_settings(settings)


@eel.expose
def get_chat_settings():
    return app_chat_fn.get_chat_settings()
