import logging

import eel
import gevent.event
import gevent.timeout

from .app.app_main import CLOSE_EVENT
from .utils import _create_js_pygame_event_dict

try:
    import pygame
    py_game_avail = 1
except ImportError:
    py_game_avail = 0


class _ControllerEvents:
    """ Keep event and result objects in this modules private namespace """
    event = gevent.event.Event()
    result = gevent.event.AsyncResult()
    joysticks = dict()


def controller_event_loop():
    """ Will be run in main eel greenlet to be able to post events to JS frontend """
    # -- Block for timeout until event is set
    _ControllerEvents.event.wait(timeout=1.0)
    _ControllerEvents.event.clear()

    # -- Get result
    try:
        event = _ControllerEvents.result.get_nowait()
    except gevent.timeout.Timeout:
        event = None

    # -- Forward result
    if event is not None:
        eel.controller_event(_create_js_pygame_event_dict(_ControllerEvents.joysticks, event))
        _ControllerEvents.result.set(None)


def _set_event_result(event):
    _ControllerEvents.result.set(event)
    _ControllerEvents.event.set()


def controller_greenlet(event_callback: callable = _set_event_result):
    """ Controller greenlet/thread receiving pygame joystick events and sending
        it to event_callback. Default callback will forward this to the main
        eel greenlet able to call the front end.
    """
    if not py_game_avail:
        logging.info('Pygame module not available')
        eel.sleep(10.0)
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
            _ControllerEvents.joysticks[j.get_instance_id()] = j

    event_loop_active = True
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
                    _ControllerEvents.joysticks[j.get_instance_id()] = j
                    # ------------------------------------------------------------------------------------
            # --- Joystick removed ---
            elif event.type == pygame.JOYDEVICEREMOVED:
                j_id = event.device_index or 0
                j = pygame.joystick.Joystick(j_id)
                if j.get_instance_id() in _ControllerEvents.joysticks:
                    logging.debug('Removing Joystick: %s', j.get_name())
                    _ControllerEvents.joysticks.pop(j.get_instance_id())
            # --- Joystick Axis moved ---
            elif event.type == pygame.JOYAXISMOTION:
                pass
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
            event_loop_active = False

        # -- End of event loop, restart to get pygame events
        eel.sleep(0.05)

    logging.info('Controller greenlet exiting.')
