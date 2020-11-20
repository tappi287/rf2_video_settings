import logging
import sys
from typing import Union, List, Optional

from .utils import JsonRepr

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)

_allowed_value_types = (bool, str, int, float)

player_adjustable_settings = {
    'Track Detail': {'name': 'Circuit Detail', 'value': 1,
                     'settings':
                         ({'value': 0, 'name': 'Low'}, {'value': 1, 'name': 'Medium'},
                          {'value': 2, 'name': 'High'}, {'value': 3, 'name': 'Full'}),
                     },
    'Player Detail': {'name': 'Player Detail', 'value': 1,
                      'settings':
                          ({'value': 0, 'name': 'Low'}, {'value': 1, 'name': 'Medium'},
                           {'value': 2, 'name': 'High'}, {'value': 3, 'name': 'Full'}),
                      },
    'Opponent Detail': {'name': 'Opponent Detail', 'value': 1,
                        'settings':
                            ({'value': 0, 'name': 'Low'}, {'value': 1, 'name': 'Medium'},
                             {'value': 2, 'name': 'High'}, {'value': 3, 'name': 'Full'}),
                        },
    'Texture Detail': {'name': 'Texture Detail', 'value': 1,
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
    'Special FX': {'name': 'Special Effects', 'value': 1,
                   'settings':
                       ({'value': 0, 'name': 'Off'}, {'value': 1, 'name': 'Low'},
                        {'value': 2, 'name': 'Medium'}, {'value': 3, 'name': 'High'}, {'value': 4, 'name': 'Ultra'}),
                   },
    'Shadows': {'name': 'Shadows', 'value': 1,
                'settings':
                    ({'value': 0, 'name': 'Off'}, {'value': 1, 'name': 'Low'},
                     {'value': 2, 'name': 'Medium'}, {'value': 3, 'name': 'High'}, {'value': 4, 'name': 'Ultra'}),
                },
    'Shadow Blur': {'name': 'Shadow Blur', 'value': 1,
                    'settings':
                        ({'value': 0, 'name': 'Off'}, {'value': 1, 'name': 'Fast'},
                         {'value': 2, 'name': 'Optimal'}, {'value': 3, 'name': 'Quality'}),
                    },
    'Soft Particles': {'name': 'Soft Particles', 'value': 1,
                       'settings':
                            ({'value': 0, 'name': 'Off'}, {'value': 1, 'name': 'Low', 'desc': 'Cheap soft edges'},
                             {'value': 2, 'name': 'High', 'desc': 'Depth buffered soft edges'}),
                       },
    'Rain FX Quality': {'name': 'Rain Drops', 'value': 1,
                        'settings':
                            ({'value': 1, 'name': 'Off'}, {'value': 2, 'name': 'Low'},
                             {'value': 3, 'name': 'Medium'}, {'value': 4, 'name': 'High'},
                             {'value': 5, 'name': 'Ultra'}),
                        },
    'Road Reflections': {'name': 'Road Reflection', 'value': 1,
                         'settings':
                            ({'value': 0, 'name': 'Off'},
                             {'value': 1, 'name': 'Low',
                              'desc': 'Reflected objects are generated for wet road and heat mirage'},
                             {'value': 2, 'name': 'High',
                              'desc': 'Reflected objects are generated for wet road and heat mirage'},
                             {'value': 3, 'name': 'Ultra', 'desc': 'Adds reflection blurring'}),
                         },
    'Environment Reflections': {'name': 'Environment Reflection', 'value': 1,
                                'settings':
                                    ({'value': 0, 'name': 'Off'},
                                     {'value': 1, 'name': 'Low',
                                      'desc': 'Live cubic mapping is used (if track and car are setup properly)'},
                                     {'value': 2, 'name': 'High',
                                      'desc': 'Live cubic mapping is used (if track and car are setup properly)'}),
                                },
}

advanced_settings = {
    'Transparency AA': {'name': 'Transparency AA', 'value': True,
                        'settings': ({'value': False, 'name': 'Disabled'},
                                     {'value': True, 'name': 'Enabled [Default]',
                                      'desc': 'Soften edges around alpha test objects'})
                        }
}

adjustable_video_settings = {
        'VrSettings': {'name': 'VR', 'value': 0, '_type': int,
                       'settings': ({'value': 0, 'name': 'Disabled'}, {'value': 1, 'name': 'HMD only'},
                                  {'value': 2, 'name': 'HMD + Mirror'})
                       },
        # 'WindowedMode': {'name': 'Windowed Mode', 'value': 0, 'hidden': True,
        #                  'settings': ({'value': 0, 'name': 'Fullscreen'}, {'value': 1, 'name': 'Windowed'})
        #                  },
        # 'Borderless': {'name': 'Borderless', 'value': 0, 'hidden': True,
        #                'settings': ({'value': 0, 'name': 'Windowed'}, {'value': 1, 'name': 'Borderless'})
        #                },
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
                                    )}
        }


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
    key = 'Base Options'
    title = 'Base Settings'

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


class GraphicOptions(BaseOptions):
    key = 'Graphic Options'
    title = 'Display Settings'

    def __init__(self):
        super(GraphicOptions, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(player_adjustable_settings)


class VideoSettings(BaseOptions):
    key = 'Video Settings'
    title = 'Video Settings'

    def __init__(self):
        super(VideoSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(adjustable_video_settings)


class AdvancedGraphicSettings(BaseOptions):
    key = 'Graphic Options'
    title = 'Advanced Display Settings'

    def __init__(self):
        super(AdvancedGraphicSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(advanced_settings)
