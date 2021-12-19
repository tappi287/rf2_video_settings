import logging

from rf2settings.gamecontroller import ControllerEvents
from rf2settings.utils import capture_app_exceptions


@capture_app_exceptions
def start_controller_capture():
    # Start receiving Controller Events including axis events for input mapping
    ControllerEvents.capturing = True

    logging.debug('Started capturing game controller events for input mapping')


@capture_app_exceptions
def stop_controller_capture():
    ControllerEvents.capturing = False

    logging.debug('Stopped capturing game controller events for input mapping')
