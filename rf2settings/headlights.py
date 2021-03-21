import logging
from typing import Optional

import gevent

from .app_settings import AppSettings
from .app.app_main import CLOSE_EVENT
from .gamecontroller import ControllerEvents, SetupControllerAxis
from .preset.settings_model import HeadlightSettings, HeadlightControllerAssignments
from .settingsdef.headlights import controller_assignments
from .rf2lights import RfactorHeadlight
from .rf2connect import RfactorConnect, RfactorState
from .utils import create_js_pygame_event_dict, capture_app_exceptions

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


class _Settings:
    """ We only update this upon launch or settings_changed event to save some calls """
    enabled = False
    flash_duration = (20, 20)
    flash_count = 4
    pit_flash_duration = (200, 200)
    pit_limiter = False
    pit_lane = False
    default_to_on = False
    on_automatically = 0

    def __init__(self):
        self.headlight_settings = HeadlightSettings()
        self.controller_assignments = HeadlightControllerAssignments()

        self.refresh()

    def refresh(self):
        self.headlight_settings = self._read_headlight_settings()
        self.controller_assignments = self._read_headlight_controller_assignments()
    
    def _read_headlight_settings(self):
        """ Called on launch or after settings_changed event to re-read
            the Headlight settings from AppSettings.
            Also caches all settings for fast access in _SettingsCache
        """
        headlight_settings = HeadlightSettings()
        headlight_settings.from_js_dict(AppSettings.headlight_settings)
    
        # -- Cache settings for fast access
        flash_on = headlight_settings.get_option('flash_on_time').value
        flash_off = headlight_settings.get_option('flash_off_time').value
        self.flash_duration = (int(flash_on), int(flash_off))
    
        pit_on = headlight_settings.get_option('pit_flash_on_time').value
        pit_off = headlight_settings.get_option('pit_flash_off_time').value
        self.pit_flash_duration = (int(pit_on), int(pit_off))
    
        self.pit_limiter = headlight_settings.get_option('pit_limiter').value
        self.pit_lane = headlight_settings.get_option('pit_lane').value
        self.default_to_on = headlight_settings.get_option('default_to_on').value
        self.on_automatically = int(headlight_settings.get_option('on_automatically').value)
        self.flash_count = int(headlight_settings.get_option('flash_count').value)
        self.enabled = headlight_settings.get_option('enabled').value
    
        return headlight_settings

    @staticmethod
    def _read_headlight_controller_assignments():
        """ Called in launch or after settings_changed event to re-read
            the Headlight Controller Assignments.
            No caching needed, this is just a dictionary wrapped in convenience class.
        """
        con_assignments = HeadlightControllerAssignments()
        con_assignments.from_js_dict(AppSettings.headlight_controller_assignments)
        _ControllerHandler.setup_axis(con_assignments)
        return con_assignments


class _ControllerHandler:
    """ Group methods and variables belonging to handling controller input """

    # -- Keep a shortcut to Controller Assignment command names just in case
    #    we ever decide to rename the command names and forget to update it here...
    #    Keys are unlikely to change..
    toggle_hdl = controller_assignments.get('toggle_headlights', dict()).get('name', str())
    flash_hdl = controller_assignments.get('flash_headlights', dict()).get('name', str())
    hdl_on = controller_assignments.get('headlights_on', dict()).get('name', str())
    hdl_off = controller_assignments.get('headlights_off', dict()).get('name', str())

    @staticmethod
    def check_controller_event(event, con_opt: HeadlightControllerAssignments) -> Optional[dict]:
        """ Check if the current Controller Event matches against any
            Headlight Controller Assignments.
        """
        toggle_cmd = con_opt.options.get('toggle_headlights')
        flash_cmd = con_opt.options.get('flash_headlights')
        on_cmd = con_opt.options.get('headlights_on')
        off_cmd = con_opt.options.get('headlights_off')

        py_event = create_js_pygame_event_dict(ControllerEvents.joysticks, event)
        _axis_trigger, _hat_trigger = False, False

        for cmd in (toggle_cmd, flash_cmd, on_cmd, off_cmd):
            # -- Check devices match
            if cmd.get('guid', 0) != py_event.get('guid'):
                continue
            # -- Check event type match
            if cmd.get('type') != py_event.get('type'):
                continue
            # -- Check axis trigger match
            if cmd.get('axis') and cmd.get('axis') >= 0 and cmd.get('axis') == py_event.get('axis'):
                c, v = cmd.get('value'), py_event.get('value')
                if 0 < v:
                    v = 1.0
                else:
                    v = -1.0
                if 0 < c < v:
                    _axis_trigger = True
                elif 0 > c > v:
                    _axis_trigger = True
                else:
                    continue
            # -- Check dpad match
            if cmd.get('hat') == py_event.get('hat') and cmd.get('value') == py_event.get('value'):
                _hat_trigger = True
            # -- Check value/button match
            if not _axis_trigger and not _hat_trigger:
                if cmd.get('value') != py_event.get('value') and cmd.get('value') != py_event.get('button'):
                    continue

            # -- We have a match!
            return cmd

    @classmethod
    def setup_axis(cls, con_opt: HeadlightControllerAssignments):
        """ Update Controller greenlet with axis and joystick instance id's we have
            a mapping for so it can ignore all other axis events.
        """
        watched_axis = dict()
        for key, opt in con_opt.options.items():
            axis = opt.get('axis')
            if not isinstance(axis, int):
                continue
            for instance_id, j in ControllerEvents.joysticks.items():
                if j.get_guid() != opt.get('guid', 0):
                    continue
                if instance_id not in watched_axis:
                    watched_axis[instance_id] = set()
                watched_axis[instance_id].add(axis)

        if watched_axis:
            for instance_id, axis in watched_axis.items():
                for a in axis:
                    logging.info('Watching Axis %s on Controller #%s', a, instance_id)
            SetupControllerAxis.watched_axis = watched_axis


# -------------------------------------------------------------------
# ---             Headlights Greenlet Event Loop                  ---
# -------------------------------------------------------------------
@capture_app_exceptions
def headlights_greenlet():
    """ Headlights greenlet event loop spawned on app launch.
        This event loop will run until app termination.
    """
    if not py_game_avail:
        logging.warning('Pygame module not available. Headlight functionality not available!')
        return

    # -- Read settings upon launch
    config = _Settings()
    con = _ControllerHandler()

    # -- Setup the RfactorConnect shared memory only once
    _setup_rfconnect = True

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
            config.refresh()
            ControllerEvents.settings_changed.clear()

            # -- Update keyboard key used to trigger headlights
            if rf2_hdl is not None:
                rf2_hdl.set_toggle_key(AppSettings.headlight_rf_key)

        # --- Headlights App En-/Disabled ---
        if not config.enabled:
            gevent.sleep(10.0)
            continue

        # --- Init rf2headlights
        if rf2_hdl is None:
            rf2_hdl = RfactorHeadlight(AppSettings.headlight_rf_key)

        # -- Update global App RfactorConnect connection state
        #    from Headlights shared memory
        if (rf2_hdl.info.sharedMemoryVerified and _setup_rfconnect) or \
                (_setup_rfconnect and RfactorConnect.state == RfactorState.ready):
            RfactorConnect.setup_shared_memory(rf2_hdl.info.isSharedMemoryAvailable)
            _setup_rfconnect = False
        if RfactorConnect.use_shared_memory:
            RfactorConnect.set_state_from_shared_memory(rf2_hdl.info.sharedMemoryVerified)

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
            if config.default_to_on:
                rf2_hdl.on()

        # -- Check Pit Limiter
        if config.pit_limiter:
            logging.debug('Headlights checking Pit Limiter')
            rf2_hdl.check_pit_limiter(config.pit_flash_duration)
        # -- Check if in pit lane
        if config.pit_lane:
            rf2_hdl.check_pit_lane(config.pit_flash_duration)

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
            controller_cmd = con.check_controller_event(event, config.controller_assignments)

        if controller_cmd is None:
            continue

        # -- Trigger Headlight flashes/toggle/on/off based on matched command
        command_name = controller_cmd.get('name')

        if command_name == con.toggle_hdl:
            logging.info('Toggling headlights %s', rf2_hdl.headlight_toggle_dik)
            rf2_hdl.toggle()
        elif command_name == con.flash_hdl:
            logging.info('Flashing headlights %s', rf2_hdl.headlight_toggle_dik)
            rf2_hdl.four_flashes(config.flash_duration, config.flash_count)
        elif command_name == con.hdl_on:
            logging.info('Turning headlights on %s', rf2_hdl.headlight_toggle_dik)
            rf2_hdl.on()
        elif command_name == con.hdl_off:
            logging.info('Turning headlights off %s', rf2_hdl.headlight_toggle_dik)
            rf2_hdl.off()
        # --
        # -- End Of Event Loop

    # -- It is unlikely that we make it here as the Controller event will block
    #    longer than it takes to terminate the app / read the CLOSE_EVENT state.
    #    There are no known problems with this behaviour so far.
    logging.info('Headlights greenlet exiting.')
