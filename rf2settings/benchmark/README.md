"""
base_url = 'localhost'
web_ui_port = 5397

Start race session: POST
/rest/race/startRace
r = RfactorConnect.post_request('/rest/race/startRace')

Drive: POST
/rest/garage/drive
r = RfactorConnect.post_request('/rest/garage/drive')

Get replay dict: GET
/rest/watch/replays

Load and play replay: GET
/rest/watch/play/<replay_id>'

Switch to fullscreen: POST (with data=None)
/navigation/action/NAV_TO_FULL_EVENT_MONITOR

Navigate to garage: POST
/navigation/action/NAV_TO_GARAGE

Next session: POST
/navigation/action/NAV_NEXT_SESSION

Switch to MAIN MENU: POST (with data=None)
/navigation/action/NAV_TO_MAIN_MENU

Quit the game: POST (with data=None)
/rest/start/quitGame

Get Tracks: GET
/rest/race/track?locale=en-US
Set Track: POST, data=track_id
/rest/race/track
Get Series GET
/rest/race/series
v1124
Set Series POST data=series_id
/rest/race/series
v1125
/rest/race/series?signature=series_id
Get Cars GET
/rest/race/car
Set Cars POST: data=car_id
/rest/race/car

SESSION SETTINGS
Get
/rest/sessions GET
Race Time
/rest/sessions/settings POST {'sessionSetting': 'SESSSET_race_starting_time', 'value': 1}
Grid Position
/rest/sessions/settings POST {'sessionSetting': 'SESSSET_Grid_Position', 'value': 1}

Get selection
/rest/race/selection?locale=en-US
Get Profile
/rest/profile
"""