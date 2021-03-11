import logging
import platform
import sys
import webbrowser

import eel

from rf2settings.app.app_dashboard import expose_dashboard_methods
from rf2settings.app.app_graphics import expose_graphics_methods
from rf2settings.app.app_controller import expose_controller_methods
from rf2settings.app.app_headlights import expose_headlights_methods
from rf2settings.app.app_main import expose_main_methods, CLOSE_EVENT
from rf2settings.app.app_multiplayer import expose_multiplayer_methods
from rf2settings.app.app_presets import expose_preset_methods
from rf2settings.app_settings import AppSettings
from rf2settings.gamecontroller import controller_greenlet, controller_event_loop
from rf2settings.headlights import headlights_greenlet
from rf2settings.runasadmin import run_as_admin

# -- Make sure eel methods are exposed at start-up
expose_main_methods()
expose_dashboard_methods()
expose_graphics_methods()
expose_multiplayer_methods()
expose_preset_methods()
expose_headlights_methods()
expose_controller_methods()

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)

# TODO: -Proper- logging setup


def start_eel():
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
    eel.spawn(controller_greenlet)

    # -- Headlights Greenlet
    eel.spawn(headlights_greenlet)

    # -- Run until window/tab closed
    while not CLOSE_EVENT.is_set():
        # Game controller event loop
        controller_event_loop()


if __name__ == '__main__':
    start_eel()
