import json
import logging
import sys
from pathlib import Path
from typing import Iterable, Tuple, Optional, Dict, Type

from .presets_dir import get_user_presets_dir, get_user_export_dir
import settings_model
from .utils import create_file_safe_name

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)


class PresetType:
    graphics = 0
    advanced_settings = 1


class BasePreset:
    # Defines which type of options this Preset represents
    preset_type: int = -1
    option_class_keys = set()

    def __init__(self, name: str = None, desc: str = None):
        """ Preset Base Type representing a set <option_class_keys> of BaseOptions
            Presets handle the loading and saving of the settings provided in BaseOptions to a JSON file.
        """
        self.name = name or 'Default'
        self.desc = desc or 'The default preset represents the settings currently found in your rFactor 2 installation.'

        # -- Set BaseOptions as Preset fields
        #    eg. Preset.video_settings: VideoSettings
        for key in self.option_class_keys:
            options_instance = settings_model.OPTION_CLASSES.get(key)()
            setattr(self, key, options_instance)

    def update(self, rf):
        """ Update current preset from the actual rFactor 2 settings on disk

        :param modules.rfactor.RfactorPlayer rf:
        :return:
        """
        # Update Graphic Options, Video Settings etc. from rF object
        for key, _ in self._iterate_options():
            setattr(self, key, getattr(rf.options, key))

        # Set Preset Name from Player Nick
        player_json_dict = rf.read_player_json_dict()
        if player_json_dict.get('DRIVER'):
            self.name = f'Current Settings [{player_json_dict["DRIVER"].get("Player Nick")}]'

    def save_unique_file(self) -> bool:
        base_name = create_file_safe_name(self.name)
        file_name = base_name
        name_idx = 0
        preset_dir = get_user_presets_dir()

        while [_ for _ in preset_dir.glob(f'{file_name}*.json')]:
            name_idx += 1
            file_name = f'{base_name}_{name_idx}'

        return self.export(file_name)

    def additional_export_operations(self):
        """ Should be overwritten in sub classes """
        pass

    def export(self, unique_name: str = None) -> bool:
        file_name = create_file_safe_name(unique_name or self.name)
        file = get_user_export_dir() / f'{file_name}.json'
        self.name = unique_name or self.name
        self.additional_export_operations()

        return self._save_to_file(file)

    def save(self) -> bool:
        file_name = create_file_safe_name(self.name)
        file = get_user_presets_dir() / f'{file_name}.json'

        return self._save_to_file(file)

    def _save_to_file(self, file) -> bool:
        try:
            with open(file.as_posix(), 'w') as f:
                json.dump(self.to_js(export=True), f, indent=2, sort_keys=True)
        except Exception as e:
            logging.fatal('Could not write Preset export! %s', e)
            return False
        return True

    def _iterate_options(self) -> Iterable[Tuple[str, settings_model.BaseOptions]]:
        """ Helper to iterate thru all BaseOptions assigned to the preset. """
        for key in self.option_class_keys:
            yield key, getattr(self, key)

    def to_js(self, export: bool = False):
        """ Convert to json serializable dictionary """
        preset_dict = {k: v.to_js(export) for k, v in self._iterate_options()}
        preset_dict['name'] = self.name
        preset_dict['desc'] = self.desc
        preset_dict['preset_type'] = self.preset_type
        return preset_dict

    def from_js_dict(self, js_dict):
        """ Update Preset object from a json dictionary """
        self.name = js_dict.get('name')
        self.desc = js_dict.get('desc')

        for key, _ in self._iterate_options():
            options_class = settings_model.OPTION_CLASSES.get(key)
            options_instance = options_class()
            options_instance.from_js_dict(js_dict.get(key, dict()))
            setattr(self, key, options_instance)

    def __eq__(self, other):
        """ Report difference between presets

        :param modules.preset.Preset other:
        :return: True if other options differ
        """
        for key, options in self._iterate_options():
            if getattr(other, key) != options:
                logging.debug('Compared Presets %s to %s. Found deviating options in %s',
                              self.name, other.name, options.title)
                return False
        return True


class GraphicsPreset(BasePreset):
    preset_type: int = PresetType.graphics
    option_class_keys = {settings_model.GraphicOptions.app_key, settings_model.AdvancedGraphicSettings.app_key,
                         settings_model.VideoSettings.app_key, settings_model.ResolutionSettings.app_key}

    def __init__(self, name: str = None, desc: str = None):
        """ Presets for graphical preferences """
        super(GraphicsPreset, self).__init__(name, desc)

    def additional_export_operations(self):
        # Reset Resolution Settings
        default_res_settings = settings_model.ResolutionSettings()
        setattr(self, settings_model.ResolutionSettings.app_key, default_res_settings)


class AdvancedSettingsPreset(BasePreset):
    preset_type: int = PresetType.advanced_settings
    option_class_keys = {settings_model.DriverOptions.app_key, settings_model.GameOptions}

    def __init__(self, name: str = None, desc: str = None):
        super(AdvancedSettingsPreset, self).__init__(name, desc)


def load_presets_from_dir(preset_dir: Path, preset_type: int = 0, current_preset: Optional[BasePreset] = None,
                          selected_preset_name: str = None):
    preset_ls, selected_preset = list(), None

    for preset_file in preset_dir.glob('*.json'):
        preset = load_preset(preset_file, preset_type)
        if not preset:
            continue
        if preset.name == selected_preset_name:
            selected_preset = preset
        if current_preset and preset and preset.name != current_preset.name:
            preset_ls.append(preset)

    return preset_ls, selected_preset


def load_preset(file: Path, load_preset_type: int) -> Optional[BasePreset]:
    try:
        with open(file.as_posix(), 'r') as f:
            new_preset_dict = json.loads(f.read())
    except Exception as e:
        logging.fatal('Could not load Preset from file! %s', e)
        return

    # -- Get type, fallback to GraphicsPreset
    preset_type = new_preset_dict.get('preset_type', PresetType.graphics)
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


PRESET_TYPES: Dict[int, Type[BasePreset]] = dict()
for preset_cls in (GraphicsPreset, AdvancedSettingsPreset):
    PRESET_TYPES[preset_cls.preset_type] = preset_cls
