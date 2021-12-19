import eel

from . import app_rfconnect_fn


def expose_rfconnect_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def quit_rfactor():
    return app_rfconnect_fn.quit_rfactor()


@eel.expose
def get_replays():
    return app_rfconnect_fn.get_replays()


@eel.expose
def get_replay_preset():
    return app_rfconnect_fn.get_replay_preset()


@eel.expose
def set_replay_preset(preset_name):
    return app_rfconnect_fn.set_replay_preset(preset_name)


@eel.expose
def play_replay(replay_name):
    return app_rfconnect_fn.play_replay(replay_name)


@eel.expose
def delete_replays(replays: list):
    return app_rfconnect_fn.delete_replays(replays)


@eel.expose
def rename_replay(replay: dict, new_name: str):
    return app_rfconnect_fn.rename_replay(replay, new_name)
