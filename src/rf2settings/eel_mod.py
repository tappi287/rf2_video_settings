import json
from pathlib import Path
from typing import List

from rf2settings.globals import get_settings_dir

EEL_JS_FILE = "eel_cache.jsc"
EEL_FUNC_NAMES_FILE = "eel_function_names.json"
EEL_JS_CLOSE_LINE = "eel.expose(closeApp)\n"
EEL_TEMPLATE_LINE = "eel.expose(_, \"{name}\")\n"


def eel_cache_dir() -> Path:
    return get_settings_dir()


def eel_names_file() -> Path:
    return eel_cache_dir() / EEL_FUNC_NAMES_FILE


def eel_cache_js_file() -> Path:
    return eel_cache_dir() / EEL_JS_FILE


def read_rf2_settings_eel_func_names() -> List[str]:
    with open(eel_names_file(), "r") as f:
        return json.load(f)


def write_rf2_settings_eel_func_names():
    """ Create eel cache with JS function names """
    import eel
    with open(eel_names_file(), "w") as f:
        json.dump(eel._js_functions, f)


def write_rf2_settings_eel_cache_js():
    with open(eel_cache_js_file(), "w") as f:
        file_content = ""
        for name in sorted(read_rf2_settings_eel_func_names()):
            file_content += EEL_TEMPLATE_LINE.format(name=name)
        file_content += EEL_JS_CLOSE_LINE
        f.write(file_content)


def prepare_eel_cache_js():
    write_rf2_settings_eel_func_names()
    write_rf2_settings_eel_cache_js()
