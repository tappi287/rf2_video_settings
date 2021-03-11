import logging

import eel

from rf2settings.gamecontroller import ControllerEvents


def expose_controller_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def start_controller_capture():
    # Start receiving Controller Events including axis events for input mapping
    ControllerEvents.capturing = True

    logging.debug('Started capturing game controller events for input mapping')


@eel.expose
def stop_controller_capture():
    ControllerEvents.capturing = False

    logging.debug('Stopped capturing game controller events for input mapping')
