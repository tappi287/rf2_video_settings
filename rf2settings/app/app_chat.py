import eel

from rf2settings.app import app_chat_fn


def expose_chat_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def save_chat_settings(settings):
    return app_chat_fn.save_chat_settings(settings)


@eel.expose
def get_chat_settings():
    return app_chat_fn.get_chat_settings()


@eel.expose
def post_chat_message(message):
    return app_chat_fn.post_chat_message(message)


@eel.expose
def install_plugin():
    return app_chat_fn.install_plugin()


@eel.expose
def uninstall_plugin():
    return app_chat_fn.uninstall_plugin()


@eel.expose
def get_plugin_version():
    return app_chat_fn.get_plugin_version()


@eel.expose
def set_youtube_username(username):
    return app_chat_fn.set_youtube_username(username)


@eel.expose
def start_youtube_chat_capture():
    return app_chat_fn.start_youtube_chat_capture()


@eel.expose
def stop_youtube_chat_capture():
    return app_chat_fn.stop_youtube_chat_capture()
