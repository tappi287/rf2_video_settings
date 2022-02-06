import eel

from . import app_presets_fn


def expose_preset_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def get_presets(preset_type: int):
    return app_presets_fn.get_presets(preset_type)


@eel.expose
def select_preset(preset_name: str, preset_type: int):
    return app_presets_fn.select_preset(preset_name, preset_type)


@eel.expose
def save_preset(preset_js_dict):
    return app_presets_fn.save_preset(preset_js_dict)


@eel.expose
def export_preset(preset_js_dict):
    return app_presets_fn.export_preset(preset_js_dict)


@eel.expose
def import_preset(preset_js_dict):
    return app_presets_fn.import_preset(preset_js_dict)


@eel.expose
def import_player_json(player_json_dict, preset_type: int):
    return app_presets_fn.import_player_json(player_json_dict, preset_type)


@eel.expose
def delete_preset(preset_name, preset_type):
    return app_presets_fn.delete_preset(preset_name, preset_type)


@eel.expose
def set_user_presets_dir(user_preset_dir):
    return app_presets_fn.set_user_presets_dir(user_preset_dir)


@eel.expose
def get_user_presets_dir_web():
    return app_presets_fn.get_user_presets_dir_web()


@eel.expose
def restore_pre_replay_preset():
    return app_presets_fn.restore_pre_replay_preset()
