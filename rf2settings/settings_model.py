import logging
import sys
from typing import Union, List, Optional, Dict, Type

from rf2settings.settingsdef import graphics, generic
from .utils import JsonRepr

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)

_allowed_value_types = (bool, str, int, float)


class OptionsTarget:
    player_json = 0
    dx_config = 1


class Option(JsonRepr):
    export_skip_keys = ['settings', 'hidden', 'ini_type']

    def __init__(self):
        self.key = 'Player JSON key'
        self.name = 'Friendly Setting Name'

        # Current value
        self.value: Union[_allowed_value_types] = None

        # Extra Attributes
        self.hidden: bool = False
        self.ini_type = None

        # Possible settings
        self.settings: tuple = tuple()

    def __eq__(self, other):
        """ Report difference between options

        :param modules.settings_model.Option other:
        :return: True if self.value if differs
        """
        if other.value != self.value or other.key != self.key:
            return False
        return True


class BaseOptions(JsonRepr):
    # Key representing the category key in player_json
    key = 'Base Options'
    # Key representing the field name for Preset and RfactorPlayer classes
    # must be unique per class!
    app_key = 'base_options'
    # Category Title to be displayed in front end
    title = 'Base Settings'
    # Target to indicate RfactorPlayer where to write these options
    # eg. OptionsTarget.player_json
    target = None

    def __init__(self, options: List[Option] = None):
        if options is None:
            options = []
        self.options: List[Option] = options

    def read_from_python_dict(self, options_dict: dict):
        self.options = list()

        for key, detail_dict in options_dict.items():
            option = Option()
            option.key = key
            option.name = detail_dict.get('name', 'Unknown')
            option.settings = tuple(detail_dict.get('settings', list()))
            option.value = detail_dict.get('value')
            option.hidden = detail_dict.get('hidden')
            option.ini_type = detail_dict.get('_type')
            self.options.append(option)

    def to_js(self, export: bool = False) -> dict:
        return {'key': self.key, 'title': self.title,
                'options': [option.to_js_object(export) for option in self.options]}

    def _get_option(self, key) -> Optional[Option]:
        o = [o for o in self.options if o.key == key]
        if o:
            return o[0]

    def from_js_dict(self, json_dict):
        for k, v in json_dict.items():
            if k == 'options':
                # -- Read only values for Option objects that already exist
                #    We assume the BaseOptions object has been initialized in it's
                #    sub-classes with valid default settings.
                for js_opt in v:
                    _k, _v = js_opt.get('key'), js_opt.get('value')
                    opt = self._get_option(_k)
                    if opt and _v is not None:
                        opt.value = _v
            else:
                setattr(self, k, v)

    def __eq__(self, other):
        """ Report difference between options

        :param modules.settings_model.BaseOptions other:
        :return: True if other options differ
        """
        if other.key != self.key:
            return False

        # -- Compare every Option
        #    sort both by their keys
        options = sorted(self.options, key=lambda k: k.key)
        other_options = sorted(other.options, key=lambda k: k.key)
        return all([a == b for a, b in zip(options, other_options)])


class DriverOptions(BaseOptions):
    key = 'DRIVER'
    app_key = 'driver_options'
    title = 'Driver Settings'
    target = OptionsTarget.player_json

    def __init__(self):
        super(DriverOptions, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(generic.driver_settings)


class GameOptions(BaseOptions):
    key = 'Game Options'
    app_key = 'game_options'
    title = 'Game Settings'
    target = OptionsTarget.player_json

    def __init__(self):
        super(GameOptions, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(generic.game_settings)


class GraphicOptions(BaseOptions):
    key = 'Graphic Options'
    app_key = 'graphic_options'
    title = 'Display Settings'
    target = OptionsTarget.player_json

    def __init__(self):
        super(GraphicOptions, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(graphics.adjustable_graphics_settings)


class VideoSettings(BaseOptions):
    key = 'Video Settings'
    app_key = 'video_settings'
    title = 'Video Settings'
    target = OptionsTarget.dx_config

    def __init__(self):
        super(VideoSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(graphics.adjustable_video_settings)


class ResolutionSettings(BaseOptions):
    key = 'Resolution Settings'
    app_key = 'resolution_settings'
    title = 'Resolution and Window Settings'
    target = OptionsTarget.dx_config

    def __init__(self):
        super(ResolutionSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(graphics.resolution_video_settings)


class AdvancedGraphicSettings(BaseOptions):
    key = 'Graphic Options'
    app_key = 'advanced_graphic_options'
    title = 'Advanced Display Settings'
    target = OptionsTarget.player_json

    def __init__(self):
        super(AdvancedGraphicSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(graphics.advanced_settings)


OPTION_CLASSES: Dict[str, Type[BaseOptions]] = dict()
for opt_class in [DriverOptions, GraphicOptions, VideoSettings,
                  ResolutionSettings, AdvancedGraphicSettings]:
    OPTION_CLASSES[opt_class.app_key] = opt_class
