import json
import logging
import sys
from pathlib import Path
from typing import Iterable, Tuple, Optional

from modules.globals import get_user_presets_dir
from modules.settings_model import GraphicOptions, AdvancedGraphicSettings, VideoSettings, BaseOptions
from modules.utils import create_file_safe_name

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)


class Preset:
    _option_base_classes = {'graphic_options': GraphicOptions,
                            'advanced_graphic_options': AdvancedGraphicSettings,
                            'video_settings': VideoSettings}

    def __init__(self, name: str = None, desc: str = None):
        self.name = name or 'Default'
        self.desc = desc or 'The default preset represents the settings currently found in your rFactor 2 installation.'
        self.graphic_options = GraphicOptions()
        self.advanced_graphic_options = AdvancedGraphicSettings()
        self.video_settings = VideoSettings()

    def update(self, rf):
        """ Update current preset from the actual rFactor 2 settings on disk

        :param modules.rfactor.RfactorPlayer rf:
        :return:
        """
        # Update Graphic Options, Video Settings etc. from rF object
        for key, _ in self._iterate_options():
            setattr(self, key, getattr(rf, key))

        # Set Preset Name from Player Nick
        json = rf.get_player_json_dict()
        if json.get('DRIVER'):
            self.name = f'Current Settings [{json["DRIVER"].get("Player Nick")}]'

    def save_unique_file(self) -> bool:
        base_name = create_file_safe_name(self.name)
        file_name = base_name
        name_idx = 0
        preset_dir = get_user_presets_dir()

        while [_ for _ in preset_dir.glob(f'{file_name}*.json')]:
            name_idx += 1
            file_name = f'{base_name}_{name_idx}'

        return self.export(file_name)

    def export(self, unique_name: str = None) -> bool:
        file_name = create_file_safe_name(unique_name or self.name)
        file = get_user_presets_dir() / f'{file_name}.json'
        self.name = unique_name or self.name

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

    def _iterate_options(self) -> Iterable[Tuple[str, BaseOptions]]:
        """ Helper to iterate thru all BaseOptions assigned to the preset. """
        for key in self._option_base_classes.keys():
            yield key, getattr(self, key)

    def to_js(self, export: bool = False):
        """ Convert to json serializable dictionary """
        preset_dict = {k: v.to_js(export) for k, v in self._iterate_options()}
        preset_dict['name'] = self.name
        preset_dict['desc'] = self.desc
        return preset_dict

    def from_js_dict(self, js_dict):
        """ Update Preset object from a json dictionary """
        self.name = js_dict.get('name')
        self.desc = js_dict.get('desc')
        for key, _ in self._iterate_options():
            options_class = self._option_base_classes.get(key)
            options_instance = options_class()
            options_instance.from_js_dict(js_dict.get(key))
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


def load_presets_from_dir(preset_dir: Path, current_preset: Preset = None, selected_preset_name: str = None):
    presets, selected_preset = list(), None

    for preset_file in preset_dir.glob('*.json'):
        preset = load_preset(preset_file)
        if not preset:
            continue
        if preset.name == selected_preset_name:
            selected_preset = preset
        if current_preset and preset and preset.name != current_preset.name:
            presets.append(preset)

    return presets, selected_preset


def load_preset(file: Path) -> Optional[Preset]:
    default_preset = Preset()
    try:
        with open(file.as_posix(), 'r') as f:
            new_preset_dict = json.loads(f.read())

            new_preset = Preset()
            new_preset.from_js_dict(new_preset_dict)

        # - Make sure older Preset Versions contain all fields
        for k, v in default_preset.__dict__.items():
            if k[:2] != '__' and not callable(v):
                if k not in new_preset.__dict__:
                    setattr(new_preset, k, v)

        return new_preset
    except Exception as e:
        logging.fatal('Could not load Preset from file! %s', e)
