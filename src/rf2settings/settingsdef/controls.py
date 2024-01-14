# JSON Category: Controls
ui_gamepad_mouse_settings = {
    'UI Gamepad Mouse - Final Speed (pixel/seconds)':
        {'name': 'Cursor Final Speed', 'value': 550,
         'settings': ({'settingType': 'range', 'min': 150, 'max': 2000, 'step': 10,
                       'desc': 'Mouse cursor final speed when controlled by D-Pad (pixel/seconds)'},)},
    'UI Gamepad Mouse - Initial Speed (pixel/seconds)':
        {'name': 'Cursor Initial Speed', 'value': 150,
         'settings': ({'settingType': 'range', 'min': 10, 'max': 2000, 'step': 10,
                       'desc': 'Mouse cursor initial speed when controlled by D-Pad (pixel/seconds)'},)},
    'UI Gamepad Mouse - Time before accelerating (seconds)':
        {'name': 'Time before accelerating', 'value': 0.5,
         'settings': ({'settingType': 'range', 'min': 0.1, 'max': 10.0, 'step': 0.1,
                       'desc': 'Mouse cursor time before starting accelerating when controlled by D-Pad (seconds)'},)},
    'UI Gamepad Mouse - Time to reach max speed (seconds)':
        {'name': 'Time to max speed', 'value': 1.5,
         'settings': ({'settingType': 'range', 'min': 0.1, 'max': 10.0, 'step': 0.1,
                       'desc': 'Mouse cursor time to reach top speed when controlled by D-Pad (seconds)'},)},
}

# Controller JSON Category: General Controls
freelook_controls = {
    'Freelook Keyboard Pitch Accel':
        {'name': 'Keyboard Pitch Accel', 'desc': 'Freelook pitch acceleration when using keyboard', 'value': 4,
         'settings': ({'settingType': 'range', 'min': 0.001, 'max': 10.0, 'step': 0.001},)
         },
    'Freelook Keyboard Pitch Decel':
        {'name': 'Keyboard Pitch Decel', 'desc': 'Freelook pitch deceleration when using keyboard', 'value': 4,
         'settings': ({'settingType': 'range', 'min': 0.001, 'max': 10.0, 'step': 0.001},)},
    'Freelook Keyboard Pitch Speed':
        {'name': 'Keyboard Pitch Speed', 'desc': 'Freelook pitch speed when using keyboard', 'value': 1.5,
         'settings': ({'settingType': 'range', 'min': 0.001, 'max': 10.0, 'step': 0.001},)},
    'Freelook Keyboard Yaw Accel':
        {'name': 'Keyboard Yaw Accel', 'desc': 'Freelook Yaw acceleration when using keyboard', 'value': 4,
         'settings': ({'settingType': 'range', 'min': 0.001, 'max': 10.0, 'step': 0.001},)},
    'Freelook Keyboard Yaw Decel':
        {'name': 'Keyboard Yaw Decel', 'desc': 'Freelook Yaw deceleration when using keyboard', 'value': 4,
         'settings': ({'settingType': 'range', 'min': 0.001, 'max': 10.0, 'step': 0.001},)},
    'Freelook Keyboard Yaw Speed':
        {'name': 'Keyboard Yaw Speed', 'desc': 'Freelook yaw speed when using keyboard', 'value': 1.5,
         'settings': ({'settingType': 'range', 'min': 0.001, 'max': 10.0, 'step': 0.001},)},
    'Freelook Mouse Pitch Speed':
        {'name': 'Mouse Pitch Speed', 'desc': 'Freelook pitch speed when using mouse', 'value': 0.004,
         'settings': ({'settingType': 'range', 'min': 0.00001, 'max': 0.1, 'step': 0.0001},)},
    'Freelook Mouse Yaw Speed':
        {'name': 'Mouse Yaw Speed', 'desc': 'Freelook yaw speed when using mouse', 'value': 0.004,
         'settings': ({'settingType': 'range', 'min': 0.00001, 'max': 0.1, 'step': 0.0001},)},
    'Freemove Down Speed':
        {'name': 'Vertical (Y) Speed', 'desc': 'Freemove Down speed', 'value': 2.0,
         'settings': ({'settingType': 'range', 'min': 0.001, 'max': 10.0, 'step': 0.001},)},
    'Freemove Forward Speed':
        {'name': 'Forward (Z) Speed', 'desc': 'Freemove Forward speed', 'value': 2.0,
         'settings': ({'settingType': 'range', 'min': 0.001, 'max': 10.0, 'step': 0.001},)},
    'Freemove Right Speed':
        {'name': 'Horizontal (X) Speed', 'desc': 'Freemove Right speed', 'value': 2.0,
         'settings': ({'settingType': 'range', 'min': 0.001, 'max': 10.0, 'step': 0.001},)},
}
# Controller JSON Category: General Controls
general_steering = {
    'Steering Wheel Maximum Rotation Default':
        {'name': 'Max Rotation Default', 'value': 900,
         'settings': ({'settingType': 'range', 'min': 40, 'max': 1440, 'step': 10,
                       'desc': 'Default maximum wheel range to use when not read from driver, '
                               'from 40 to 1440 degrees'},)},
    'Steering Wheel Range':
        {'name': 'Wheel Range', 'value': 524,
         'settings': ({'settingType': 'range', 'min': 40, 'max': 1440, 'step': 10,
                       'desc': 'Degrees of steering wheel rotation, both visual and physical (if available)'},)},
    'Steering Wheel Maximum Rotation from Driver':
        {'name': 'Max Rotation from Driver', 'value': True,
         'desc': 'Whether to read the steering wheel rotation from the wheel driver, if possible',
         'settings': ({'value': True, 'name': 'On [Default]'},
                      {'value': False, 'name': 'Off'})
         },
    'Steering Wheel Software Rotation':
        {'name': 'Software Rotation', 'value': False,
         'desc': 'Whether to limit the maximum steering wheel rotation in software',
         'settings': (
             {'value': True, 'name': 'On'}, {'value': False, 'name': 'Off [Default]'})
         }
}
# Controller JSON Category: Input
benchmark_rfactor = {
    'Control - Toggle AI Control': {'name': 'Toggle AI Control', 'value': [0, 40], },
    'Control - Framerate': {'name': 'Toggle FPS Counter', 'value': [0, 49], },
}