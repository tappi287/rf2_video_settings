import sys
import logging
from pathlib import Path
from typing import Iterable, Tuple, Optional

import jsonpickle

from modules.globals import get_presets_dir
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

    def save_unique_file(self):
        base_name = create_file_safe_name(self.name)
        file_name = base_name
        name_idx = 0
        preset_dir = get_presets_dir()

        while [_ for _ in preset_dir.glob(f'{file_name}*.json')]:
            name_idx += 1
            file_name = f'{base_name}_{name_idx}'

        self.save(file_name)

    def save(self, unique_name: str = None) -> bool:
        """ Save the preset to the application settings dir
            as jsonpickled python object.
        """
        file_name = create_file_safe_name(unique_name or self.name)
        preset_dir = get_presets_dir()
        file = preset_dir / f'{file_name}.json'

        try:
            with open(file.as_posix(), 'w') as f:
                f.write(jsonpickle.encode(self))
        except Exception as e:
            logging.fatal('Could not save Preset! %s', e)
            return False
        return True

    def _iterate_options(self) -> Iterable[Tuple[str, BaseOptions]]:
        """ Helper to iterate thru all BaseOptions assigned to the preset. """
        for key in self._option_base_classes.keys():
            yield key, getattr(self, key)

    def to_js(self):
        """ Convert to json serializable dictionary """
        preset_dict = {k: v.to_js() for k, v in self._iterate_options()}
        preset_dict['name'] = self.name
        preset_dict['desc'] = self.desc
        return preset_dict

    def from_js_dict(self, js_dict):
        """ Update Preset object from a json dictionary """
        self.name = js_dict.get('name')
        self.desc = js_dict.get('desc')
        for key, _ in self._iterate_options():
            base_class = self._option_base_classes.get(key)
            options_obj = base_class()
            options_obj.from_js_dict(js_dict.get(key))
            setattr(self, key, options_obj)

    def __eq__(self, other):
        """ Report difference between presets

        :param modules.preset.Preset other:
        :return: False if other options differ
        """
        for key, options in self._iterate_options():
            if getattr(other, key) != options:
                logging.debug('Compared Presets %s to %s. Found deviating options in %s',
                              self.name, other.name, options.title)
                return False
        return True


def load_preset(file: Path) -> Optional[Preset]:
    default_preset = Preset()
    try:
        with open(file.as_posix(), 'r') as f:
            new_preset = jsonpickle.decode(f.read())

        # Migrate if changes to Preset class happened
        if type(new_preset) is dict:
            new_preset_obj = Preset()
            new_preset_obj.from_js_dict(new_preset)
            new_preset = new_preset_obj

        # - Make sure older Preset Versions contain all fields
        for k, v in default_preset.__dict__.items():
            if k[:2] != '__' and not callable(v):
                if k not in new_preset.__dict__:
                    setattr(new_preset, k, v)

        return new_preset
    except Exception as e:
        logging.fatal('Could not load Preset from file! %s', e)
