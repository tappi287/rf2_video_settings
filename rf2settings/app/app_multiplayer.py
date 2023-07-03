import eel

from . import app_multiplayer_fn


def expose_multiplayer_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def get_server_list(only_favourites: bool = False):
    return app_multiplayer_fn.get_server_list(only_favourites)


@eel.expose
def refresh_server(address: list):
    return app_multiplayer_fn.refresh_server(address)


@eel.expose
def get_server_browser_settings():
    return app_multiplayer_fn.get_server_browser_settings()


@eel.expose
def save_server_browser_settings(server_browser: dict):
    return app_multiplayer_fn.save_server_browser_settings(server_browser)


@eel.expose
def get_server_favourites():
    return app_multiplayer_fn.get_server_favourites()


@eel.expose
def get_custom_server():
    return app_multiplayer_fn.get_custom_server()


@eel.expose
def custom_server(server_info, add: bool = True):
    return app_multiplayer_fn.custom_server(server_info, add)


@eel.expose
def server_favourite(server_info, add: bool = True):
    return app_multiplayer_fn.server_favourite(server_info, add)
