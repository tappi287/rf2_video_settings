from typing import Union, List

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
                            ({'value': 0, 'name': 'Off'}, {'value': 1, 'name': 'Low'},
                             {'value': 2, 'name': 'Medium'}, {'value': 3, 'name': 'High'}),
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


class Option:
    def __init__(self):
        self.key = 'Player JSON key'
        self.name = 'Friendly Setting Name'

        # Current value
        self.value: Union[_allowed_value_types] = None

        # Possible settings
        self.settings: tuple = tuple()

    def to_js_object(self):
        return {'key': self.key, 'name': self.name, 'value': self.value, 'settings': list(self.settings)}


class BaseOptions:
    key = 'Base Options'
    title = 'Base Settings'

    def __init__(self, options: List = None):
        if options is None:
            options = []
        self.options = options

    def read_from_python_dict(self, options_dict: dict):
        self.options = list()

        for key, detail_dict in options_dict.items():
            option = Option()
            option.key = key
            option.name = detail_dict.get('name', 'Unknown')
            option.settings = tuple(detail_dict.get('settings', list()))
            option.value = detail_dict.get('value')
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


class Preset:
    def __init__(self, name: str = None, graphic_options: GraphicOptions = None):
        if name is None:
            name = 'Default'
        if graphic_options is None:
            graphic_options = GraphicOptions()
        self.name = name
        self.graphic_options = graphic_options

    def to_js(self):
        return {'name': self.name, 'graphic_options': self.graphic_options.to_js()}

    def from_js_dict(self, js_dict):
        self.name = js_dict.get('name')
        self.graphic_options.from_js_dict(js_dict.get('graphic_options'))
