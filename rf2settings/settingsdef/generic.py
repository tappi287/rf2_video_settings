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
