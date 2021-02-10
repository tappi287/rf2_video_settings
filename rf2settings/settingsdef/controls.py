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
