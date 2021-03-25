# AppSettings headlights
headlight_settings = {
    'enabled': {'name': 'Enable App Headlights', 'value': False,
                'desc': 'Enable the control of your in-game headlights thru this applications '
                        'rf2headlights functionality',
                'settings': ({'value': True, 'name': 'On'}, {'value': False, 'name': 'Off'})
                },
    'on_automatically': {'name': 'Automatic Headlights', 'value': 0,
                         'settings':
                             ({'value': 0, 'name': 'Manual', 'desc': 'Driver turns headlights permanently on or off'},
                              {'value': 1, 'name': 'One Driver',
                               'desc': 'Enable headlights if at least one other driver has them on'},
                              {'value': 2, 'name': 'Two Drivers',
                               'desc': 'Enable headlights if more than one other driver has them on'},
                              {'value': 3, 'name': 'Half Grid',
                               'desc': 'Enable headlights if at least half of the other drivers have them on'},
                              {'value': 4, 'name': 'All',
                               'desc': 'Enable headlights if all the other drivers have them on'},
                              ),
                         },
    'default_to_on': {'name': 'Headlights on at start', 'value': False,
                      'desc': 'Automatically turn headlights on when a session started',
                      'settings': ({'value': True, 'name': 'On'}, {'value': False, 'name': 'Off'})
                      },
    'pit_limiter': {'name': 'Pit Limiter Auto Flash', 'value': False,
                            'desc': 'Flash headlights whenever the pit limiter is on',
                            'settings': ({'value': True, 'name': 'On'}, {'value': False, 'name': 'Off'})
                    },
    'pit_lane': {'name': 'Pit Lane Auto Flash', 'value': False,
                 'desc': 'Flash headlights whenever the vehicle is in the pit lane',
                 'settings': ({'value': True, 'name': 'On'}, {'value': False, 'name': 'Off'})
                 },
    'flash_count': {'name': 'Overtake Flash Count', 'value': 4,
                    'desc': 'How many times to flash when triggering headlight flash.',
                    'settings': ({'settingType': 'range', 'min': 2, 'max': 24, 'step': 1,
                                  'desc': ''},)
                    },
    'flash_on_time': {'name': 'Overtake Flash ON Time', 'value': 50,
                      'desc': 'Length of one flash in milliseconds',
                      'settings': ({'settingType': 'range', 'min': 40, 'max': 500, 'step': 10,
                                    'desc': ''},)
                      },
    'flash_off_time': {'name': 'Overtake Flash OFF Time', 'value': 90,
                       'desc': 'Length of the break between flashes in milliseconds',
                       'settings': ({'settingType': 'range', 'min': 40, 'max': 500, 'step': 10,
                                     'desc': ''},)
                       },
    'pit_flash_on_time': {'name': 'Pit Flash ON Time', 'value': 100,
                          'desc': 'Length of one flash in milliseconds',
                          'settings': ({'settingType': 'range', 'min': 50, 'max': 500, 'step': 10,
                                        'desc': ''},)
                          },
    'pit_flash_off_time': {'name': 'Pit Flash OFF Time', 'value': 200,
                           'desc': 'Length of the break between flashes in milliseconds',
                           'settings': ({'settingType': 'range', 'min': 50, 'max': 500, 'step': 10,
                                         'desc': ''},)
                           },
}

controller_assignments = {
    # eg. Dpad Motion
    'toggle_headlights': {'name': 'Toggle Headlights', 'desc': 'Controller mapping to switch '
                                                               'the Headlights on and off.',
                          'device_name': 'Xbox One S Controller',
                          'guid': '', 'type': 1538, 'hat': 1, 'value': [0, -1],
                          'axis': None},
    # eg. Button 8 down
    'flash_headlights': {'name': 'Flash Headlights', 'desc': 'App Controller mapping to trigger '
                                                             'flashing Headlights.',
                         'device_name': 'Xbox One S Controller',
                         'guid': '', 'type': 1539, 'hat': None, 'value': 8, 'axis': None},
    'headlights_on': {'name': 'Headlights On', 'desc': 'App Controller mapping to turn Headlights on. (No toggle)',
                      'device_name': 'Xbox One S Controller',
                      'guid': '', 'type': 1539, 'hat': None, 'value': 8, 'axis': None},
    'headlights_off': {'name': 'Headlights Off', 'desc': 'App Controller mapping to turn Headlights off. (No toggle)',
                       'device_name': 'Xbox One S Controller',
                       'guid': '', 'type': 1539, 'hat': None, 'value': 8, 'axis': None},
}

headlight_rfactor = {
    'Control - Headlights': {'name': 'Toggle Headlights', 'value': [0, 35],
                             'desc': 'rFactor 2 Headlight control key/button',
                             },
}

auto_headlight_rfactor = {
    'Auto Headlights': {'name': 'Auto Headlights', 'value': True,
                        'desc': 'Adds an automatic options and set it to the default setting. Automatically turn on and'
                                ' off headlights dependent on weather conditions.',
                        'settings': ({'value': True, 'name': 'On'}, {'value': False, 'name': 'Off'})
                        }
}