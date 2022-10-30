import logging
import platform
import sys
import webbrowser

import eel
import gevent

from rf2settings.app import expose_app_methods
from rf2settings.app.app_main import CLOSE_EVENT, close_callback, restore_backup
from rf2settings.app_settings import AppSettings
from rf2settings.gamecontroller import controller_greenlet, controller_event_loop
from rf2settings.globals import FROZEN
from rf2settings.headlights import headlights_greenlet
from rf2settings.log import setup_logging
from rf2settings.rf2greenlet import rfactor_greenlet, rfactor_event_loop
from rf2settings.chat.ytgreenlet import youtube_eventloop, youtube_greenlet
from rf2settings.runasadmin import run_as_admin
from rf2settings.utils import AppExceptionHook

# -- Make sure eel methods are exposed at start-up
expose_app_methods()

# -- Setup logging
setup_logging()


def start_eel(npm_serve=True):
    logging.info('\n\n\n')
    logging.info('#######################################################')
    logging.info('################ Starting APP               ###########')
    logging.info('#######################################################\n\n\n')
    logging.info(f'Args: {sys.argv}')

    if FROZEN:
        npm_serve = False
        # Set Exception hook
        sys.excepthook = AppExceptionHook.exception_hook

    # -- Restore Mode
    if len(sys.argv) > 1 and sys.argv[1] == '-b':
        logging.warning(f'Found restore mode argument. Beginning to restore rFactor 2 settings.')
        restore_backup()
        logging.warning('\nFinished Restore Mode. Exiting application.')
        return

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
    host = 'localhost'
    page = 'index.html'
    port = 8123

    if npm_serve:
        # Dev env with npm run serve
        page = {'port': 8080}
        eel.init('vue/src')
    else:
        # Frozen or npm run build
        eel.init('web')

    # TODO: fetch OSError port in use
    try:
        eel.start(page, host=host, port=port, block=False, close_callback=close_callback)
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

    # -- YouTUbe Greenlet
    yg = eel.spawn(youtube_greenlet)

    # -- Run until window/tab closed
    while not CLOSE_EVENT.is_set():
        # Game controller event loop
        controller_event_loop()
        # rFactor 2 event loop
        rfactor_event_loop()
        # YouTube live chat event loop
        youtube_eventloop()
        # Capture exception events
        AppExceptionHook.exception_event_loop()

    # -- Shutdown Greenlets
    logging.debug('Shutting down Greenlets.')
    gevent.joinall((cg, hg, rg, yg), timeout=15.0, raise_error=True)


if __name__ == '__main__':
    start_eel()

    # -- Shutdown logging
    logging.info('\n\n\n')
    logging.info('#######################################################')
    logging.info('################ APP SHUTDOWN               ###########')
    logging.info('#######################################################\n\n\n')
    logging.shutdown()
