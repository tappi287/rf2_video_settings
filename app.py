import logging
import platform
import sys
import webbrowser

import eel
import gevent

from rf2settings.log import setup_logging
from rf2settings.app.app_controller import expose_controller_methods
from rf2settings.app.app_dashboard import expose_dashboard_methods
from rf2settings.app.app_graphics import expose_graphics_methods
from rf2settings.app.app_headlights import expose_headlights_methods
from rf2settings.app.app_main import expose_main_methods, CLOSE_EVENT
from rf2settings.app.app_multiplayer import expose_multiplayer_methods
from rf2settings.app.app_presets import expose_preset_methods
from rf2settings.app.app_replays import expose_replay_methods
from rf2settings.app_settings import AppSettings
from rf2settings.gamecontroller import controller_greenlet, controller_event_loop
from rf2settings.globals import FROZEN
from rf2settings.headlights import headlights_greenlet
from rf2settings.rf2connect import rfactor_greenlet, rfactor_event_loop
from rf2settings.runasadmin import run_as_admin
from rf2settings.utils import AppExceptionHook, capture_app_exceptions

# -- Make sure eel methods are exposed at start-up
expose_main_methods()
expose_dashboard_methods()
expose_graphics_methods()
expose_multiplayer_methods()
expose_preset_methods()
expose_headlights_methods()
expose_controller_methods()
expose_replay_methods()

# -- Setup logging
setup_logging()


@capture_app_exceptions
def test_exception():
    if AppExceptionHook.produce_exception:
        AppExceptionHook.produce_exception = False
        AppExceptionHook.test_exception()


def start_eel():
    logging.info('\n\n\n')
    logging.info('#######################################################')
    logging.info('################ Starting APP               ###########')
    logging.info('#######################################################\n\n\n')

    if FROZEN:
        # Set Exception hook
        sys.excepthook = AppExceptionHook.exception_hook

    AppSettings.load()
    AppSettings.copy_default_presets()
    AppSettings.delete_current_settings_presets()

    # This will ask for and re-run with admin rights
    # if setting needs_admin set.
    if AppSettings.needs_admin and not run_as_admin():
        return

    """
        THIS WILL DISABLE ctypes support! But it will make sure "Launch rFactor2" 
        or basically any executable that is loading DLLs will work.
    """
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.SetDllDirectoryA(None)
    """
        //
    """
    page = 'index.html'
    host = 'localhost'
    port = 8123
    eel.init('web')

    # TODO: fetch OSError port in use
    try:
        eel.start(page, host=host, port=port, block=False)
    except EnvironmentError:
        # If Chrome isn't found, fallback to Microsoft Edge on Win10 or greater
        if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:
            eel.start(page, mode='edge', host=host, port=port, block=False)
        # Fallback to opening a regular browser window
        else:
            eel.start(page, mode=None, app_mode=False, host=host, port=port, block=False)
            # Open system default web browser
            webbrowser.open_new(f'http://{host}:{port}')

    # -- Game Controller Greenlet
    cg = eel.spawn(controller_greenlet)

    # -- Headlights Greenlet
    hg = eel.spawn(headlights_greenlet)

    # -- rFactor Greenlet
    rg = eel.spawn(rfactor_greenlet)

    # -- Run until window/tab closed
    while not CLOSE_EVENT.is_set():
        # Game controller event loop
        controller_event_loop()
        # rFactor 2 event loop
        rfactor_event_loop()
        # Capture exception events
        AppExceptionHook.exception_event_loop()
        test_exception()

    # -- Shutdown Greenlets
    logging.debug('Shutting down Greenlets.')
    gevent.joinall((cg, hg, rg), timeout=15.0)

    # -- Shutdown logging
    logging.info('\n\n\n')
    logging.info('#######################################################')
    logging.info('################ APP SHUTDOWN               ###########')
    logging.info('#######################################################\n\n\n')
    logging.shutdown()


if __name__ == '__main__':
    start_eel()
