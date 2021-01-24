from pathlib import Path

from .globals import _get_user_doc_dir, check_and_create_dir, SETTINGS_DIR_NAME, EXPORT_DIR_NAME


class PresetDir:
    """ Will be set by AppSettings upon load if we have a custom value set. """
    value = str()


def get_user_presets_dir() -> Path:
    if PresetDir.value:
        return Path(PresetDir.value)
    docs_dir = _get_user_doc_dir()
    return Path(check_and_create_dir(docs_dir / SETTINGS_DIR_NAME))


def get_user_export_dir() -> Path:
    preset_dir = get_user_presets_dir()
    return Path(check_and_create_dir(preset_dir / EXPORT_DIR_NAME))
