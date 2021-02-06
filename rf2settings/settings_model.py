import logging
import sys
from typing import Union, List, Optional, Dict, Type

from .utils import JsonRepr

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)

_allowed_value_types = (bool, str, int, float)

driver_settings = {
    'Player Name': {'name': 'User Name', 'value': ''},
    'Player Nick': {'name': 'Nickname', 'value': ''}
}

adjustable_graphics_settings = {
    'Track Detail': {'name': 'Circuit Detail', 'value': 2,
                     'settings':
                         ({'value': 0, 'name': 'Low'}, {'value': 1, 'name': 'Medium'},
                          {'value': 2, 'name': 'High'}, {'value': 3, 'name': 'Full'}),
                     },
    'Player Detail': {'name': 'Player Detail', 'value': 3,
                      'settings':
                          ({'value': 0, 'name': 'Low'}, {'value': 1, 'name': 'Medium'},
                           {'value': 2, 'name': 'High'}, {'value': 3, 'name': 'Full'}),
                      },
    'Opponent Detail': {'name': 'Opponent Detail', 'value': 2,
                        'settings':
                            ({'value': 0, 'name': 'Low'}, {'value': 1, 'name': 'Medium'},
                             {'value': 2, 'name': 'High'}, {'value': 3, 'name': 'Full'}),
                        },
    'Texture Detail': {'name': 'Texture Detail', 'value': 3,
                       'settings':
                           ({'value': 0, 'name': 'Low'}, {'value': 1, 'name': 'Medium'},
                            {'value': 2, 'name': 'High'}, {'value': 3, 'name': 'Full'}),
                       },
    'Texture Filter': {'name': 'Texture Filter', 'value': 4,
                       'settings':
                           ({'value': 0, 'name': 'Bilinear'}, {'value': 1, 'name': 'Trilinear'},
                            {'value': 2, 'name': 'x2 Anisotropic'}, {'value': 3, 'name': 'x4 Anisotropic'},
                            {'value': 4, 'name': 'x8 Anisotropic'}, {'value': 5, 'name': 'x16 Anisotropic'}),
                       },
    'Special FX': {'name': 'Special Effects', 'value': 4,
                   'settings':
                       ({'value': 0, 'name': 'Off'},
                        {'value': 1, 'name': 'Low', 'perf': 'G+0,18% C+0,00%'},
                        {'value': 2, 'name': 'Medium'}, {'value': 3, 'name': 'High'},
                        {'value': 4, 'name': 'Ultra', 'perf': 'G+0,90% C+2,20%'}),
                   },
    'Shadows': {'name': 'Shadows', 'value': 3,
                'settings':
                    ({'value': 0, 'name': 'Off'}, {'value': 1, 'name': 'Low'},
                     {'value': 2, 'name': 'Medium'}, {'value': 3, 'name': 'High'}, {'value': 4, 'name': 'Ultra'}),
                },
    'Shadow Blur': {'name': 'Shadow Blur', 'value': 2,
                    'settings':
                        ({'value': 0, 'name': 'Off'}, {'value': 1, 'name': 'Fast'},
                         {'value': 2, 'name': 'Optimal'}, {'value': 3, 'name': 'Quality'}),
                    },
    'Soft Particles': {'name': 'Soft Particles', 'value': 1,
                       'settings':
                            ({'value': 0, 'name': 'Off'}, {'value': 1, 'name': 'Low', 'desc': 'Cheap soft edges'},
                             {'value': 2, 'name': 'High', 'desc': 'Depth buffered soft edges',
                              'perf': 'G+0,57% C+2,57%'}),
                       },
    'Rain FX Quality': {'name': 'Rain Drops', 'value': 3,
                        'settings':
                            ({'value': 1, 'name': 'Off', 'desc': 'Anything else than off will have a massive '
                                                                 'performance impact!'},
                             {'value': 2, 'name': 'Low', 'perf': 'G+4,10% C+6,30%'},
                             {'value': 3, 'name': 'Medium'}, {'value': 4, 'name': 'High'},
                             {'value': 5, 'name': 'Ultra', 'perf': 'G+17,2% C+6,70%'}),
                        },
    'Road Reflections': {'name': 'Road Reflection', 'value': 2,
                         'settings':
                            ({'value': 0, 'name': 'Off',
                              'desc': 'It will be hard to spot wet track areas! '
                                      'The Low setting is free on GPU but CPU heavy'},
                             {'value': 1, 'name': 'Low',
                              'desc': 'Reflected objects are generated '
                                      'for wet road and heat mirage',
                              'perf': 'G+0,33% C+5,39%'},
                             {'value': 2, 'name': 'High',
                              'desc': 'Reflected objects are generated for wet road and heat mirage'},
                             {'value': 3, 'name': 'Ultra',
                              'desc': 'Adds reflection blurring',
                              'perf': 'G+6,40% C+9,40%'}),
                         },
    'Environment Reflections': {'name': 'Environment Reflection', 'value': 2,
                                'settings':
                                    ({'value': 0, 'name': 'Off'},
                                     {'value': 1, 'name': 'Low',
                                      'desc': 'Live cubic mapping is used '
                                              '(if track and car are setup properly)',
                                      'perf': 'G+0,00% C+0,00%'},
                                     {'value': 2, 'name': 'High',
                                      'desc': 'Live cubic mapping is used '
                                              '(if track and car are setup properly)',
                                      'perf': 'G+3,39% C+4,45%'}),
                                },
}

advanced_settings = {
    'Transparency AA': {'name': 'Transparency AA', 'value': True,
                        'settings': ({'value': False, 'name': 'Disabled'},
                                     {'value': True, 'name': 'Enabled [Default]',
                                      'desc': 'Soften edges around alpha test objects'})
                        },
    'Heat FX Fade Speed': {'name': 'Heat FX Fade Speed', 'value': 30,
                           'settings': ({'value': 30, 'name': '30 [Default]',
                                         'desc': 'Speed at which exhaust heat effects reduce '
                                                 'by half (0 to completely disable)'},
                                        {'value': 0, 'name': '0',
                                         'desc': 'Fixes visual artefact bubble behind certain cars in VR.'},
                                        )
                           },
    'Max Visible Vehicles': {'name': 'Visible Vehicles', 'value': 12,
                             'settings': ({'settingType': 'range', 'min': 5, 'max': 50,
                                           'desc': 'rFactor 2 default setting: 12'}, )},
    'Rearview Particles': {'name': 'Rearview Particles', 'value': True,
                           'settings': ({'value': False, 'name': 'Disabled'},
                                        {'value': True, 'name': 'Enabled [Default]', 'perf': 'G+3,30% C+1,44%',
                                         'desc': 'Show particles like rain spray in the rear view mirror'})
                           },
    'Rearview_Back_Clip': {'name': 'Rearview Back Clip', 'value': 0,
                           'settings': ({'settingType': 'range', 'min': 0, 'max': 250,
                                         'desc': 'Back plane distance for mirror (0.0 = use default for scene)'}, )},
}

adjustable_video_settings = {
    'VrSettings': {'name': 'VR', 'value': 0, '_type': int,
                   'settings': ({'value': 0, 'name': 'Disabled'}, {'value': 1, 'name': 'HMD only'},
                                {'value': 2, 'name': 'HMD + Mirror'})
                   },
    'FSAA': {'name': 'Anti Aliasing', 'value': 0, '_type': int,
             'settings': ({'value': 0, 'name': 'Off'},
                          {'value': 32, 'name': 'Level 1', 'desc': '2x [2x Multisampling]'},
                          {'value': 33, 'name': 'Level 2', 'desc': '2xQ [2x Quincunx (blurred)]'},
                          {'value': 34, 'name': 'Level 3', 'desc': '4x [4x Multisampling]'},
                          {'value': 35, 'name': 'Level 4', 'desc': '8x [8x CSAA (4 color + 4 cv samples)]'},
                          {'value': 36, 'name': 'Level 5', 'desc': '16x [16x CSAA (4 color + 12 cv samples)]'},
                          # {'value': 32, 'name': 'Level 6', 'desc': '8xQ [8x Multisampling]'},
                          # {'value': 32, 'name': 'Level 7', 'desc': '16xQ [16x CSAA (8 color + 8 cv samples)]'},
                          # {'value': 32, 'name': 'Level 8', 'desc': '32x [32x CSAA (8 color + 24 cv samples)]'},
                          )
             },
    'EPostProcessingSettings': {'name': 'Post Effects', 'value': 1, '_type': int,
                                'settings': ({'value': 1, 'name': 'Off'},
                                             {'value': 2, 'name': 'Low', 'desc': 'Glare Effects'},
                                             {'value': 3, 'name': 'Medium', 'desc': 'Glare Effects and Depth of Field'},
                                             {'value': 4, 'name': 'High', 'desc': 'All Effects at High Quality'},
                                             {'value': 5, 'name': 'Ultra', 'desc': 'All Effects at Ultra Quality'},
                                )},
    'UseFXAA': {'name': 'FXAA', 'value': 0, '_type': int,
                'settings': ({'value': 0, 'name': 'Off'},
                             {'value': 1, 'name': 'On', 'desc': 'Cheap post processing filter to smooth '
                                                                'high contrast edges.'})},
    }

resolution_video_settings = {
    'WindowedMode': {'name': 'Windowed Mode', 'value': None, 'hidden': True,
                     'settings': ({'value': 0, 'name': 'Fullscreen'}, {'value': 1, 'name': 'Windowed'})
                     },
    'Borderless': {'name': 'Borderless', 'value': None, 'hidden': True,
                   'settings': ({'value': 0, 'name': 'Windowed'}, {'value': 1, 'name': 'Borderless'})
                   },
    'VideoMode': {'name': 'Resolution', 'value': None, 'hidden': True,
                  'settings': ({'value': 125, 'name': 'FullHD'}, )
                  },
    'VideoRefresh': {'name': 'Refresh Rate', 'value': None, 'hidden': True,
                     'settings': ({'value': 1, 'name': '60Hz'}, )
                     },
    }


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
        self.read_from_python_dict(driver_settings)


class GraphicOptions(BaseOptions):
    key = 'Graphic Options'
    app_key = 'graphic_options'
    title = 'Display Settings'
    target = OptionsTarget.player_json

    def __init__(self):
        super(GraphicOptions, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(adjustable_graphics_settings)


class VideoSettings(BaseOptions):
    key = 'Video Settings'
    app_key = 'video_settings'
    title = 'Video Settings'
    target = OptionsTarget.dx_config

    def __init__(self):
        super(VideoSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(adjustable_video_settings)


class ResolutionSettings(BaseOptions):
    key = 'Resolution Settings'
    app_key = 'resolution_settings'
    title = 'Resolution and Window Settings'
    target = OptionsTarget.dx_config

    def __init__(self):
        super(ResolutionSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(resolution_video_settings)


class AdvancedGraphicSettings(BaseOptions):
    key = 'Graphic Options'
    app_key = 'advanced_graphic_options'
    title = 'Advanced Display Settings'
    target = OptionsTarget.player_json

    def __init__(self):
        super(AdvancedGraphicSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(advanced_settings)


OPTION_CLASSES: Dict[str, Type[BaseOptions]] = dict()
for opt_class in [DriverOptions, GraphicOptions, VideoSettings,
                  ResolutionSettings, AdvancedGraphicSettings]:
    OPTION_CLASSES[opt_class.app_key] = opt_class
