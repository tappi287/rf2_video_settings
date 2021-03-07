import logging
from typing import Optional

import gevent

from .app_settings import AppSettings
from .app.app_main import CLOSE_EVENT
from .gamecontroller import ControllerEvents
from .preset.settings_model import HeadlightSettings, HeadlightControllerAssignments
from .settingsdef.headlights import controller_assignments
from .rf2lights import RfactorHeadlight
from .utils import create_js_pygame_event_dict

try:
    import pygame
    py_game_avail = 1
except ImportError:
    py_game_avail = 0

# -- Headlight Greenlet Update rate in float seconds
#    Controller Events will wait for UPDATE_RATE but trigger instantaneous updates when needed.
#
#    rf2 Player not driving or Esc pressed/track unloaded will trigger
#    a UPDATE_RATE * 2 sleep period.
UPDATE_RATE = 0.2


class _SettingsCache:
    """ We only update this upon launch or settings_changed event to save some calls """
    enabled = False
    flash_duration = (20, 20)
    flash_count = 4
    pit_flash_duration = (200, 200)
    pit_limiter = False
    pit_lane = False
    default_to_on = False
    on_automatically = 0


class _CmdNameCache:
    """ Keep a shortcut to Controller Assignment command names just in case
        we ever decide to rename the command names and forget to update
        it here...
        Keys are unlikely to change..
    """
    toggle_hdl = controller_assignments.get('toggle_headlights', dict()).get('name', str())
    flash_hdl = controller_assignments.get('flash_headlights', dict()).get('name', str())
    hdl_on = controller_assignments.get('headlights_on', dict()).get('name', str())
    hdl_off = controller_assignments.get('headlights_off', dict()).get('name', str())


def _read_headlight_settings():
    """ Called on launch or after settings_changed event to re-read
        the Headlight settings from AppSettings.
        Also caches all settings for fast access in _SettingsCache
    """
    headlight_settings = HeadlightSettings()
    headlight_settings.from_js_dict(AppSettings.headlight_settings)

    # -- Cache settings for fast access
    flash_on = headlight_settings.get_option('flash_on_time').value
    flash_off = headlight_settings.get_option('flash_off_time').value
    _SettingsCache.flash_duration = (int(flash_on), int(flash_off))

    pit_on = headlight_settings.get_option('pit_flash_on_time').value
    pit_off = headlight_settings.get_option('pit_flash_off_time').value
    _SettingsCache.pit_flash_duration = (int(pit_on), int(pit_off))

    _SettingsCache.pit_limiter = headlight_settings.get_option('pit_limiter').value
    _SettingsCache.pit_lane = headlight_settings.get_option('pit_lane').value
    _SettingsCache.default_to_on = headlight_settings.get_option('default_to_on').value
    _SettingsCache.on_automatically = int(headlight_settings.get_option('on_automatically').value)
    _SettingsCache.flash_count = int(headlight_settings.get_option('flash_count').value)
    _SettingsCache.enabled = headlight_settings.get_option('enabled').value

    return headlight_settings


def _read_headlight_controller_assignments():
    """ Called in launch or after settings_changed event to re-read
        the Headlight Controller Assignments.
        No caching needed, this is just a dictionary wrapped in convenience class.
    """
    con_assignments = HeadlightControllerAssignments()
    con_assignments.from_js_dict(AppSettings.headlight_controller_assignments)
    return con_assignments


def check_controller_event(event, con_opt: HeadlightControllerAssignments) -> Optional[dict]:
    """ Check if the current Controller Event matches against any
        Headlight Controller Assignments.
    """
    toggle_cmd = con_opt.options.get('toggle_headlights')
    flash_cmd = con_opt.options.get('flash_headlights')
    on_cmd = con_opt.options.get('headlights_on')
    off_cmd = con_opt.options.get('headlights_off')

    py_event = create_js_pygame_event_dict(ControllerEvents.joysticks, event)

    for cmd in (toggle_cmd, flash_cmd, on_cmd, off_cmd):
        # -- Check devices match
        if cmd.get('guid', 0) != py_event.get('guid'):
            continue
        # -- Check event type match
        if cmd.get('type') != py_event.get('type'):
            continue
        # -- Check value/button match
        if cmd.get('value') != py_event.get('value') and cmd.get('value') != py_event.get('button'):
            continue

        # -- We have a match!
        return cmd


# -------------------------------------------------------------------
# ---             Headlights Greenlet Event Loop                  ---
# -------------------------------------------------------------------
def headlights_greenlet():
    """ Headlights greenlet event loop spawned on app launch.
        This event loop will run until app termination.
    """
    if not py_game_avail:
        logging.warning('Pygame module not available. Headlight functionality not available!')
        return

    # -- Read settings upon launch
    headlight_settings = _read_headlight_settings()
    controller_opt = _read_headlight_controller_assignments()

    # -- This will be our rf2headlights instance if needed
    rf2_hdl = None
    # -- Keep track if player is driving for the first time
    _player_is_driving = False

    event_loop_active = True
    while event_loop_active:
        # --- QUIT ---
        if CLOSE_EVENT.is_set():
            logging.info('Headlights greenlet received CLOSE event.')
            event_loop_active = False

        # --- Re-read settings if needed ---
        if ControllerEvents.settings_changed.is_set():
            logging.info('Headlight greenlet is re-reading headlight_settings')
            headlight_settings = _read_headlight_settings()
            controller_opt = _read_headlight_controller_assignments()
            ControllerEvents.settings_changed.clear()

            # -- Update keyboard key used to trigger headlights
            if rf2_hdl is not None:
                rf2_hdl.set_toggle_key(AppSettings.headlight_rf_key)

        # --- Headlights App En-/Disabled ---
        if not headlight_settings.get_option('enabled').value:
            gevent.sleep(10.0)
            continue

        # --- Init rf2headlights
        if rf2_hdl is None:
            rf2_hdl = RfactorHeadlight(AppSettings.headlight_rf_key)

        # ------ RF2 Headlights functionality --------
        # --------------------------------------------
        # -- Player is not on track
        if not rf2_hdl.player_is_driving():
            _player_is_driving = False
            rf2_hdl.stop_flashing()
            gevent.sleep(UPDATE_RATE * 2)
            continue

        # -- Player pressed Esc or rFactor has no focus
        if rf2_hdl.esc_check():
            gevent.sleep(UPDATE_RATE * 2)
            continue

        # -- Check automatic headlight
        if not _player_is_driving:
            # First time player takes control
            _player_is_driving = True
            if _SettingsCache.default_to_on:
                rf2_hdl.on()

        # -- Check Pit Limiter
        if _SettingsCache.pit_limiter:
            rf2_hdl.check_pit_limiter(_SettingsCache.pit_flash_duration)
        # -- Check if in pit lane
        if _SettingsCache.pit_lane:
            rf2_hdl.check_pit_lane(_SettingsCache.pit_flash_duration)

        # --- Wait for Controller events ---
        event_found = ControllerEvents.event.wait(UPDATE_RATE)
        if not event_found:
            continue

        # -- Get Controller event result
        try:
            event = ControllerEvents.result.get_nowait()
        except gevent.timeout.Timeout:
            event = None

        # -- Check if controller event matches any assigned controller commands
        controller_cmd = None
        if event is not None:
            controller_cmd = check_controller_event(event, controller_opt)

        if controller_cmd is None:
            continue

        # -- Trigger Headlight flashes/toggle/on/off based on matched command
        command_name = controller_cmd.get('name')

        if command_name == _CmdNameCache.toggle_hdl:
            logging.info('Toggling headlights %s', rf2_hdl.headlight_toggle_dik)
            rf2_hdl.toggle()
        elif command_name == _CmdNameCache.flash_hdl:
            logging.info('Flashing headlights %s', rf2_hdl.headlight_toggle_dik)
            rf2_hdl.four_flashes(_SettingsCache.flash_duration, _SettingsCache.flash_count)
        elif command_name == _CmdNameCache.hdl_on:
            logging.info('Turning headlights on %s', rf2_hdl.headlight_toggle_dik)
            rf2_hdl.on()
        elif command_name == _CmdNameCache.hdl_off:
            logging.info('Turning headlights off %s', rf2_hdl.headlight_toggle_dik)
            rf2_hdl.on()
        # --
        # -- End Of Event Loop

    # -- It is unlikely that we make it here as the Controller event will block
    #    longer than it takes to terminate the app / read the CLOSE_EVENT state.
    #    There are no known problems with this behaviour so far.
    logging.info('Headlights greenlet exiting.')
