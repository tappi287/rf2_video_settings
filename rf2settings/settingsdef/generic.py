# JSON Category: DRIVER
driver_settings = {
    'Player Name': {'name': 'User Name', 'value': ''},
    'Player Nick': {'name': 'Nickname', 'value': ''}
}
# JSON Category: Game Options
game_settings = {
    'Auto-change Opponent List': {'name': 'Auto Opponent List', 'value': True,
                                  'desc': 'Whether to change the single-player allowed vehicle '
                                          'filter when player changes vehicles',
                                  'settings': ({'value': True, 'name': 'On [Default]'}, {'value': False, 'name': 'Off'})
                                  },
    'Relative Fuel Strategy': {'name': 'Fuel Strategy', 'value': True,
                               'desc': 'Show how much fuel to ADD, rather than how much TOTAL fuel to fill the tank up '
                                       'to (note: new default is ADD)',
                               'settings': ({'value': True, 'name': 'Add [Default]',
                                             'desc': 'Pit Crew will ADD the requested amount of fuel'},
                                            {'value': False, 'name': 'Fill up',
                                             'desc': 'Pit Crew will fill fuel up UNTIL the requested amount'})
                               },
    'Compress Replay': {'name': 'Compress Replay', 'value': 1,
                        'desc': '0 (none) to 4 (highest); how much to compress VCR file (uses less disk space but '
                                'takes more time to write when a session ends)',
                        'settings': ({'settingType': 'range', 'min': 0, 'max': 4, 'step': 1,
                                      'desc': '0 (none) to 4 (highest); how much to compress VCR file (uses less disk '
                                              'space but takes more time to write when a session ends)'},)
                        },
    'Auto Skip Garaged Vehicles': {'name': 'Auto Skip Garage', 'value': False,
                                   'desc': 'If On, vehicles in garage stalls will be skipped when cycling cameras. '
                                           'Set this value to 0 to see all vehicles; the left shift key can be held '
                                           'while cycling to dynamically suspend auto skipping.',
                                   'settings': ({'value': True, 'name': 'On'},
                                                {'value': False, 'name': 'Off [Default]'})
                                   },
    'Damper Units': {'name': 'Damper Units', 'value': False,
                     'desc': 'Display dampers (shocks) in garage as: number setting (e.g. 1-20), '
                             'or rate (e.g. 1000-9000 Nm/s)',
                     'settings': ({'value': True, 'name': 'Rate in Nm/s'},
                                  {'value': False, 'name': 'Number [Default]'})
                     },
    'RealTimeLogging': {'name': 'RealTime Logging', 'value': 0,
                        'settings': ({'value': 0, 'name': 'Off [Default]'},
                                     {'value': 1, 'name': 'Accurate'})
                        },
    'Inactive Sleep Time': {'name': 'Inactive Sleep Time', 'value': 25,
                            'settings': ({'settingType': 'range', 'min': 0, 'max': 500, 'step': 1,
                                          'desc': 'Number of milliseconds to sleep each message loop if the game is '
                                                  'not the active application (-1 to disable). Will give more CPU '
                                                  'to other apps when minimized, etc.'},)},
}
# JSON Category: Miscellaneous
misc_settings = {
    'WebUI port': {'name': 'WebUI port', 'value': 5397,

                   'settings': ({'settingType': 'range', 'min': 1024, 'max': 99999, 'step': 1,
                                 'desc': 'Port for the WebUI'},)
                   },
    'enable UI Keyboard Nav': {'name': 'UI Keyboard Nav', 'value': 0,
                               'desc': 'Enables keyboard navigation (enter forwards, esc backwards) through the UI',
                               'settings': ({'value': 0, 'name': 'Disabled'},
                                            {'value': 1, 'name': 'Enabled'})
                               },
}

# App specific controller assignments
app_controller_assignments = {
    'quit_rfactor': {'name': 'Quit rFactor 2', 'desc': 'Use a controller button to quit rFactor.',
                     'device_name': 'Xbox One S Controller',
                     'guid': '', 'type': 1539, 'hat': None, 'value': None, 'axis': None},
}

# Benchmark settings
benchmark_settings = {
    'Length': {'key': 'BenchmarkLength', 'name': 'Benchmark Length', 'value': 50,
               'settings': ({'settingType': 'range', 'min': 10, 'max': 200, 'step': 1,
                             'desc': 'Recording Length in Seconds'}, )},
}
# Settings set via WebUI
session_ui_settings = {
    'SESSSET_Grid_Position': {'name': 'Grid Position', 'value': 15,
                              'settings': ({'settingType': 'range', 'min': 0, 'max': 99, 'step': 1,
                                            'display': 'position'},)},
    'SESSSET_AI_Strength': {'name': 'AI Strength', 'value': 20,
                            'settings': ({'settingType': 'range', 'min': 10, 'max': 120, 'step': 1, },)}
}
# Content Settings set via WebUi
content_ui_settings = {
    'series': {'name': 'Series', 'value': None},
    'tracks': {'name': 'Tracks', 'value': None},
    'location': {'name': 'Location', 'value': None},
    'layout': {'name': 'Layout', 'value': None},
    'manufacturer': {'name': 'Manufacturer', 'value': None},
    'model': {'name': 'Model', 'value': None},
    'cars': {'name': 'Cars', 'value': None},
}

# Benchmark specific: Game Options
session_settings = {
    'GPRIX Opponents': {'name': 'GRPRIX Opponents', 'value': 25, 'desc': 'Number of Opponents',
                        '_dupl': ['CHAMP Opponents', 'CURNT Opponents'],
                        'settings': ({'settingType': 'range', 'min': 0, 'max': 99, 'step': 1, },)},
    'Exit Confirmation': {'name': 'Exit Confirmation', 'value': 0,
                          'desc': '0=none, 1=race only, 2=always',
                          'settings': ({'value': 0, 'name': 'Never'},
                                       {'value': 1, 'name': 'Race Only [Default]'},
                                       {'value': 2, 'name': 'Always'})},
}
# Benchmark specific: Race Conditions
session_conditions = {
    'GPRIX Weather': {'name': 'Simple Weather', 'value': 3,
                      'desc': '0=sun, 1=clouds, 2=rain, 3=default, 4=random, 5=scripted',
                      'settings': ({'value': 0, 'name': 'Sunny'},
                                   {'value': 1, 'name': 'Clouds'},
                                   {'value': 2, 'name': 'Rain'},
                                   {'value': 3, 'name': 'Default'},
                                   {'value': 4, 'name': 'Random'},
                                   {'value': 5, 'name': 'Scripted'},)
                      },
    'GPRIX RaceStartingTime': {'name': 'Race Starting Time', 'value': 840,
                               '_dupl': 'CURNT RaceStartingTime',
                               'settings': ({'settingType': 'range', 'min': 0, 'max': 1440, 'step': 30,
                                             'display': 'time'},)},
    'GPRIX Num Qual Sessions': {'name': 'Num Qualy Sessions', 'value': 0,
                                'settings': ({'settingType': 'range', 'min': 0, 'max': 4, 'step': 1, },)},
    'GPRIX Num Race Sessions': {'name': 'Num Race Sessions', 'value': 1,
                                'settings': ({'settingType': 'range', 'min': 1, 'max': 4, 'step': 1, },)},
    'Run Practice1': {'name': 'Run Practice 1', 'value': False,
                      'desc': '',
                      'settings': ({'value': True, 'name': 'On'},
                                   {'value': False, 'name': 'Off'})},
    'Run Practice2': {'name': 'Run Practice 2', 'value': False,
                      'desc': '',
                      'settings': ({'value': True, 'name': 'On'},
                                   {'value': False, 'name': 'Off'})},
    'Run Practice3': {'name': 'Run Practice 3', 'value': False,
                      'desc': '',
                      'settings': ({'value': True, 'name': 'On'},
                                   {'value': False, 'name': 'Off'})},
    'Run Practice4': {'name': 'Run Practice 4', 'value': False,
                      'desc': '',
                      'settings': ({'value': True, 'name': 'On'},
                                   {'value': False, 'name': 'Off'})},
    'Run Warmup':    {'name': 'Run Warmup', 'value': False,
                      'desc': '',
                      'settings': ({'value': True, 'name': 'On'},
                                   {'value': False, 'name': 'Off'})},
}
