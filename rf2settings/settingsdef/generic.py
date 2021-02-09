# JSON Category: DRIVER
driver_settings = {
    'Player Name': {'name': 'User Name', 'value': ''},
    'Player Nick': {'name': 'Nickname', 'value': ''}
}
# JSON Category: Game Options
game_settings = {
    'Auto-change Opponent List': {'name': 'Auto-change Opponent List', 'value': True,
                                  'desc': 'Whether to change the single-player allowed vehicle '
                                          'filter when player changes vehicles',
                                  'settings': ({'value': True, 'name': 'On [Default]'}, {'value': False, 'name': 'Off'})
                                  },
    'Relative Fuel Strategy': {'name': 'Fuel Strategy', 'value': True,
                               'desc': 'Show how much fuel to ADD, rather than how much TOTAL fuel to fill the tank up '
                                       'to (note: new default is true)',
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
}
