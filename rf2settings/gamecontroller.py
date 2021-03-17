import json
import logging
from time import time

import eel
import gevent.event
import gevent.timeout

from .app.app_main import CLOSE_EVENT
from .utils import create_js_pygame_event_dict

try:
    import pygame
    py_game_avail = 1
except ImportError:
    py_game_avail = 0


class SetupControllerAxis:
    AXIS_DEADZONE = 0.35
    AXIS_DEBOUNCE = 300 / 1000  # Check axis again after debounce interval
    AXIS_TRIGGER_VALUE = 0.5
    watched_axis = dict()


class ControllerEvents:
    """ Keep event and result objects in this modules namespace """
    event = gevent.event.Event()
    result = gevent.event.AsyncResult()
    settings_changed = gevent.event.Event()
    joysticks = dict()
    capturing = False  # When we want to capture input mappings and capture all axis events as well


def controller_event_loop():
    """ Will be run in main eel greenlet to be able to post events to JS frontend """
    # -- Block for timeout until event is set
    event_found = ControllerEvents.event.wait(timeout=2.0)

    if event_found:
        ControllerEvents.event.clear()

        # -- Get result
        try:
            event = ControllerEvents.result.get_nowait()
        except gevent.timeout.Timeout:
            event = None

        # -- Forward result
        if event is not None:
            eel.controller_event(
                json.dumps(create_js_pygame_event_dict(ControllerEvents.joysticks, event), ensure_ascii=False)
            )


def _set_event_result(event):
    ControllerEvents.result.set(event)
    ControllerEvents.event.set()


def controller_greenlet(event_callback: callable = _set_event_result):
    """ Controller greenlet/thread receiving pygame joystick events and sending
        it to event_callback. Default callback will forward this to the controller_event_loop
        eel greenlet able to call the front end.
    """
    if not py_game_avail:
        logging.info('Pygame module not available')
        gevent.sleep(10.0)
        return

    pygame.init()
    pygame.event.set_blocked(pygame.MOUSEMOTION)

    # Initialize the _ControllerEvents.joysticks.
    pygame.joystick.init()

    # -- Get an initial set of Joystick devices
    #    +we have to keep a reference to the Joystick objects or we will not receive events
    if pygame.joystick.get_init():
        for j_id in range(pygame.joystick.get_count()):
            j = pygame.joystick.Joystick(j_id)
            j.init()
            logging.info('Found PyGame Joystick device %s: %s %s', j_id, j.get_name(), j.get_instance_id())
            ControllerEvents.joysticks[j.get_instance_id()] = j

    event_loop_active = True
    # When input is triggered by an axis we will not trigger an event again
    # until it is back below it's deadzone value + debounce timer
    a = SetupControllerAxis
    axis_triggered, axis_debounce = False, time()
    while event_loop_active:
        for event in pygame.event.get():
            # --- Joystick added ---
            if event.type == pygame.JOYDEVICEADDED:
                j_id = event.device_index or 0
                j = pygame.joystick.Joystick(j_id)
                j.init()

                if not j.get_init():
                    logging.error('Error initializing Joystick: %s', j_id)
                else:
                    logging.debug('Initialized Joystick: %s', j.get_name())
                    # ------------------------------------------------------------------------------------
                    # We have to keep a reference to the Joystick objects or we will not receive events.
                    ControllerEvents.joysticks[j.get_instance_id()] = j
                    # ------------------------------------------------------------------------------------
            # --- Joystick removed ---
            elif event.type == pygame.JOYDEVICEREMOVED:
                valid_ids = set()
                for j_id in range(pygame.joystick.get_count()):
                    j = pygame.joystick.Joystick(j_id)
                    valid_ids.add(j.get_instance_id())
                invalid_ids = set(ControllerEvents.joysticks.keys()).difference(valid_ids)
                for invalid_id in invalid_ids:
                    ControllerEvents.joysticks.pop(invalid_id)
                    logging.debug('Removed Joystick device with instance id: %s', invalid_id)
            # --- Joystick Axis moved ---
            elif event.type == pygame.JOYAXISMOTION:
                if ControllerEvents.capturing:
                    if abs(event.value) > a.AXIS_DEADZONE:
                        logging.info('Axis event %s %s', event.type, event)
                        event_callback(event)
                else:
                    if event.instance_id in a.watched_axis and event.axis in a.watched_axis.get(event.instance_id):
                        if (time() - axis_debounce) > a.AXIS_DEBOUNCE:
                            if abs(event.value) > a.AXIS_DEADZONE and not axis_triggered:
                                axis_triggered = True
                                axis_debounce = time()
                                event_callback(event)
                            if abs(event.value) < a.AXIS_DEADZONE:
                                axis_triggered = False
            # --- Joystick Button pressed ---
            elif event.type == pygame.JOYBUTTONDOWN:
                event_callback(event)
            # --- Joystick button released ---
            elif event.type == pygame.JOYBUTTONUP:
                pass
            # --- Joystick Dpad motion ---
            elif event.type == pygame.JOYHATMOTION:
                event_callback(event)
            # --- Keyboard Key pressed ---
            elif event.type == pygame.KEYDOWN:
                event_callback(event)

        # --- QUIT ---
        if CLOSE_EVENT.is_set():
            logging.info('Controller greenlet received CLOSE event.')
            # Wake up greenlets waiting for controller events
            event_callback(None)
            event_loop_active = False

        # -- End of event loop, restart to get pygame events
        gevent.sleep(0.02)

    logging.info('Controller greenlet exiting.')
