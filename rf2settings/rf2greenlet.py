""" Connect to rFactor 2 Ui via it's rest api """
import logging

import eel

from .app.app_main import CLOSE_EVENT
from .app_settings import AppSettings
from rf2settings.benchmark import RfactorBenchmark
from .rf2command import Command, CommandQueue
from .rf2connect import RfactorState, RfactorConnect
from .rf2events import RfactorLiveEvent, RfactorQuitEvent, RfactorStatusEvent, BenchmarkProgressEvent
from .utils import capture_app_exceptions


def _rfactor_greenlet_loop():
    # -- Receive Quit rFactor Event from FrontEnd
    if RfactorQuitEvent.event.is_set():
        CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=10.0))
        CommandQueue.append(Command(Command.quit, timeout=10.0))
        # -- Reset Quit Event
        RfactorQuitEvent.reset()

    # -- If we were live before, re-apply previous graphics preset
    if RfactorLiveEvent.changed_from_live():
        # -- Moved to a FrontEnd call so Presets refresh
        #    and Preset restore will not happen in parallel in different greenlets
        pass

    # -- Report wait for processes shut down
    if RfactorConnect.state == RfactorState.waiting_for_process:
        RfactorStatusEvent.set('Waiting for shut down of rFactor 2 processes.')

    # -- Update rFactor Live State
    if RfactorConnect.state != RfactorState.unavailable and not RfactorLiveEvent.was_live:
        # -- Report state change to frontend
        RfactorLiveEvent.set(True)

        # -- Set Session Settings if present in AppSettings
        if AppSettings.session_selection and AppSettings.apply_webui_settings:
            CommandQueue.append(Command(Command.set_session_settings, data=AppSettings.session_selection,
                                        timeout=5.0))
            # -- Reset stored Session Settings
            AppSettings.session_selection = dict()

        # -- Set Content Selection if present in AppSettings
        if AppSettings.content_selected and AppSettings.apply_webui_settings:
            CommandQueue.append(Command(Command.set_content, data=AppSettings.content_selected, timeout=5.0))
            # -- Reset stored Content Selection
            AppSettings.content_selected = dict()

        AppSettings.apply_webui_settings = False
        AppSettings.save()

        # -- Get Content
        if CommandQueue.is_empty():
            CommandQueue.append(Command(Command.get_content, timeout=10.0))

        RfactorConnect.set_to_active_timeout()
    elif RfactorConnect.state == RfactorState.unavailable:
        # -- Report state change to frontend
        RfactorLiveEvent.set(False)

    # ---------------------------
    # -- COMMAND QUEUE
    # ---------------------------
    CommandQueue.run()


@capture_app_exceptions
def rfactor_greenlet():
    logging.info('rFactor Greenlet started.')
    RfactorConnect.start_request_thread()
    rfb = RfactorBenchmark()

    while True:
        # -- App functionality
        _rfactor_greenlet_loop()
        # -- Benchmark functionality
        rfb.event_loop()

        close = CLOSE_EVENT.wait(timeout=RfactorConnect.active_timeout)
        if close:
            logging.info('rFactor Greenlet received CLOSE event.')
            break

    RfactorConnect.stop_request_thread()
    logging.info('rFactor Greenlet exiting')


@capture_app_exceptions
def rfactor_event_loop():
    """ Will be run in main eel greenlet to be able to post events to JS frontend """
    if RfactorLiveEvent.event.is_set():
        is_live = RfactorLiveEvent.get_nowait()
        # -- Update rFactor live state to front end
        if is_live is not None:
            eel.rfactor_live(is_live)

    if RfactorStatusEvent.event.is_set():
        status = RfactorStatusEvent.get_nowait()
        # -- Update rFactor status message in front end
        if status is not None:
            eel.rfactor_status(status)

        RfactorStatusEvent.reset()

    if BenchmarkProgressEvent.event.is_set():
        progress = BenchmarkProgressEvent.get_nowait()
        if progress is not None:
            eel.benchmark_progress(progress)
        BenchmarkProgressEvent.reset()
