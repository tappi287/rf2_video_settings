import logging
import os
import sys
import webbrowser
from pathlib import Path

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


def in_restore_mode() -> bool:
    """ Return True if App is started in Restore Mode """
    if len(sys.argv) > 1 and sys.argv[1] == '-b':
        logging.warning('Found restore mode argument. Beginning to restore rFactor 2 settings.')
        restore_backup()
        logging.warning('\nFinished Restore Mode. Exiting application.')
        return True
    return False


def prepare_app_start() -> bool:
    """ Return True if npm_serve should be used """
    logging.info('\n\n\n')
    logging.info('#######################################################')
    logging.info('################ Starting APP               ###########')
    logging.info('#######################################################\n\n\n')
    logging.info(f'Args: {sys.argv}')

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

    AppSettings.load()
    AppSettings.copy_default_presets()
    AppSettings.delete_current_settings_presets()

    if FROZEN:
        # Set Exception hook
        sys.excepthook = AppExceptionHook.exception_hook
        return False
    return True


def _main_app_loop():
    # -- Game Controller Greenlet
    cg = eel.spawn(controller_greenlet)

    # -- Headlights Greenlet
    hg = eel.spawn(headlights_greenlet)

    # -- rFactor Greenlet
    rg = eel.spawn(rfactor_greenlet)

    # -- YouTUbe Greenlet
    yg = eel.spawn(youtube_greenlet)

    # -- Run until window/tab closed
    logging.debug('Entering Event Loop')
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


def start_eel(npm_serve=True):
    # This will ask for and re-run with admin rights
    # if setting needs_admin set.
    if AppSettings.needs_admin and not run_as_admin():
        return

    host = 'localhost'
    page = 'index.html'
    port = 8123

    if npm_serve:
        # Dev env with npm run serve
        page = {'port': 8080}
        url_port = page.get('port')
        eel.init('vue/src')
    else:
        # Frozen or npm run build
        url_port = port
        eel.init('web')

    edge_cmd = f"{os.path.expandvars('%PROGRAMFILES(x86)%')}\\Microsoft\\Edge\\Application\\msedge.exe"
    start_url = f'http://{host}:{url_port}'

    try:
        app_module_prefs = getattr(AppSettings, 'app_preferences', dict()).get('appModules', list())
        if Path(edge_cmd).exists() and 'edge_preferred' in app_module_prefs:
            eel.start(page, mode='custom', host=host, port=port, block=False,
                      cmdline_args=[edge_cmd, '--profile-directory=Default', f'--app={start_url}'])
        else:
            eel.start(page, host=host, port=port, block=False, close_callback=close_callback)
    except EnvironmentError:
        # If Chrome isn't found, fallback to Microsoft Chromium Edge
        if Path(edge_cmd).exists():
            logging.info('Falling back to Edge Browser')
            eel.start(page, mode='custom', host=host, port=port, block=False,
                      cmdline_args=[edge_cmd, '--profile-directory=Default', f'--app={start_url}'])
        # Fallback to opening a regular browser window
        else:
            logging.info('Falling back to default Web Browser')
            eel.start(page, mode=None, app_mode=False, host=host, port=port, block=False)
            # Open system default web browser
            webbrowser.open_new(start_url)

    _main_app_loop()


if __name__ == '__main__':
    if not in_restore_mode():
        start_eel(prepare_app_start())

    # -- Shutdown logging
    logging.info('\n\n\n')
    logging.info('#######################################################')
    logging.info('################ APP SHUTDOWN               ###########')
    logging.info('#######################################################\n\n\n')
    logging.shutdown()
