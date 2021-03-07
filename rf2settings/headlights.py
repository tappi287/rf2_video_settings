import logging

import gevent

from .app_settings import AppSettings
from .app.app_main import CLOSE_EVENT
from .gamecontroller import ControllerEvents
from .preset.settings_model import HeadlightSettings, HeadlightControllerAssignments

try:
    import pygame
    py_game_avail = 1
except ImportError:
    py_game_avail = 0


def _read_headlight_settings():
    headlight_settings = HeadlightSettings()
    headlight_settings.from_js_dict(AppSettings.headlight_settings)
    return headlight_settings


def _read_headlight_controller_assignments():
    controller_assignments = HeadlightControllerAssignments()
    controller_assignments.from_js_dict(AppSettings.headlight_controller_assignments)
    return controller_assignments


def headlights_greenlet():
    """ Headlights greenlet """
    if not py_game_avail:
        logging.info('Pygame module not available')
        gevent.sleep(10.0)
        return

    headlight_settings = _read_headlight_settings()
    controller_opt = _read_headlight_controller_assignments()

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

        # --- Headlights App En-/Disabled ---
        if not headlight_settings.get_option('enabled').value:
            gevent.sleep(10.0)
            continue

        # --- Wait for Controller events ---
        event_found = ControllerEvents.event.wait()
        if not event_found:
            continue

        # -- Get result
        try:
            event = ControllerEvents.result.get_nowait()
        except gevent.timeout.Timeout:
            event = None

        if event is not None:
            logging.info('Headlights received controller event: %s', event)

        # -- End of event loop, restart to get pygame events
        gevent.sleep(0.01)

    logging.info('Headlights greenlet exiting.')
