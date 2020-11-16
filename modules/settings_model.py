import logging
import sys
from pathlib import Path
from typing import Union, List, Optional

import jsonpickle

from modules.globals import get_presets_dir

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)
jsonpickle.set_preferred_backend('json')

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


class Option:
    def __init__(self):
        self.key = 'Player JSON key'
        self.name = 'Friendly Setting Name'

        # Current value
        self.value: Union[_allowed_value_types] = None
        self.hidden: bool = False

        self.ini_type = None

        # Possible settings
        self.settings: tuple = tuple()

    def to_js_object(self):
        return {'key': self.key, 'name': self.name, 'value': self.value, 'hidden': self.hidden,
                'settings': list(self.settings)}


class BaseOptions:
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

    def to_js(self):
        return {'key': self.key, 'title': self.title, 'options': [option.to_js_object() for option in self.options]}

    def from_js_dict(self, js_dict):
        self.options = list()
        self.key = js_dict.get('key', 'Unknown_Key')
        self.title = js_dict.get('title', 'Unknown_Title')

        for option_dict in js_dict.get('options', list()):
            option = Option()
            option.key = option_dict.get('key')
            option.name = option_dict.get('name', 'Unknown')
            option.settings = option_dict.get('settings', tuple())
            option.value = option_dict.get('value')
            self.options.append(option)


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


class Preset:
    def __init__(self, name: str = None):
        if name is None:
            name = 'Default'

        self.name = name
        self.graphic_options = GraphicOptions()
        self.advanced_graphic_options = AdvancedGraphicSettings()
        self.video_settings = VideoSettings()

    def update(self, rf):
        """ Update current preset from the actual rFactor 2 player.JSON

        :param modules.rfactor.RfactorPlayer rf:
        :return:
        """
        self.graphic_options = rf.graphic_options
        self.advanced_graphic_options = rf.advanced_graphic_options
        self.video_settings = rf.video_settings

        json = rf.get_player_json_dict()
        if json.get('DRIVER'):
            self.name = f'Current Settings [{json["DRIVER"].get("Player Nick")}]'

    def save(self) -> bool:
        file = get_presets_dir() / f'{self.name}.json'

        try:
            with open(file.as_posix(), 'w') as f:
                f.write(jsonpickle.encode(self))
        except Exception as e:
            logging.fatal('Could not save Preset! %s', e)
            return False
        return True

    def to_js(self):
        return {'name': self.name, 'graphic_options': self.graphic_options.to_js(),
                'advanced_graphic_options': self.advanced_graphic_options.to_js(),
                'video_settings': self.video_settings.to_js()}

    def from_js_dict(self, js_dict):
        self.name = js_dict.get('name')
        self.graphic_options.from_js_dict(js_dict.get('graphic_options'))
        self.advanced_graphic_options.from_js_dict(js_dict.get('advanced_graphic_options'))
        self.video_settings.from_js_dict(js_dict.get('video_settings'))


def load_preset(file: Path) -> Optional[Preset]:
    default_preset = Preset()
    try:
        with open(file.as_posix(), 'r') as f:
            new_preset = jsonpickle.decode(f.read())

        # - Make sure older Preset Versions contain all fields
        for k, v in default_preset.__dict__.items():
            if k[:2] != '__' and not callable(v):
                if k not in new_preset.__dict__:
                    setattr(new_preset, k, v)

        return new_preset
    except Exception as e:
        logging.fatal('Could not load application settings! %s', e)
