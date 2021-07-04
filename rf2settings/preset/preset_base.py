import json
import logging
from pathlib import Path
from typing import Dict, Type, Optional

from . import preset
from .settings_model import OptionsTarget
from ..globals import find_subclasses

PRESET_TYPES: Dict[int, Type[preset.BasePreset]] = dict()
for name, preset_cls in find_subclasses(preset, preset.BasePreset):
    PRESET_TYPES[preset_cls.preset_type] = preset_cls
del preset_cls


def load_presets_from_dir(preset_dir, preset_type: int, current_preset: Optional[preset.BasePreset]=None,
                          selected_preset_name=None):
    """ Load all Presets from a directory of a certain type

    :param Path preset_dir: Directory to search in
    :param int preset_type: Preset Type
    :param rf2settings.preset.BasePreset current_preset: optional current preset
    :param str selected_preset_name: optional currently selected preset name
    :return: Tuple[List[rf2settings.preset.BasePreset], Optional[rf2settings.preset.BasePreset]]
    """
    preset_ls, selected_preset = list(), None

    for preset_file in preset_dir.glob('*.json'):
        preset_obj = load_preset(preset_file, preset_type)
        if not preset_obj:
            continue
        if preset_obj.name == selected_preset_name:
            selected_preset = preset_obj
        if current_preset and preset_obj and preset_obj.name != current_preset.name:
            preset_ls.append(preset_obj)

        # -- Make sure we read WebUi Options for Current Preset from Preset file
        #    Because these options can not be read from the rF installation.
        if current_preset and preset_obj and preset_obj.name == current_preset.name:
            webui_opt = {k: o for k, o in preset_obj.iterate_options()
                         if o.target in (OptionsTarget.webui_session, OptionsTarget.webui_content)}
            if webui_opt:
                for key, options in webui_opt.items():
                    setattr(current_preset, key, options)

    return preset_ls, selected_preset


def load_preset(file: Path, load_preset_type: int) -> Optional[preset.BasePreset]:
    """

    :param file:
    :param load_preset_type:
    :return: Optional[rf2settings.preset.BasePreset]
    """
    try:
        with open(file.as_posix(), 'r') as f:
            new_preset_dict: dict = json.loads(f.read())
    except Exception as e:
        logging.fatal('Could not load Preset from file! %s', e)
        return

    # -- Get type
    preset_type = new_preset_dict.get('preset_type', None)

    # -- Check JSON is actually a preset file
    if preset_type is None:
        test_keys = {'desc', 'name', 'title'}
        if test_keys.difference(new_preset_dict.keys()):
            logging.error('%s was not identified as valid preset file.', file.name)
            return

        # -- Fallback to GraphicsPreset
        preset_type = preset.PresetType.graphics

    # -- Skip Presets that are not of the desired type
    if load_preset_type != preset_type:
        return

    # -- Create new preset instance based on type
    new_preset = PRESET_TYPES.get(preset_type)()

    # -- Load preset options from json
    new_preset.from_js_dict(new_preset_dict)

    # - Make sure older Preset Versions contain all fields
    for k, v in PRESET_TYPES.get(preset_type)().__dict__.items():
        if k[:2] != '__' and not callable(v):
            if k not in new_preset.__dict__:
                setattr(new_preset, k, v)

    return new_preset
