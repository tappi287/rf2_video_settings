""" Connect to rFactor 2 Ui via it's rest api """
import logging

import eel
import gevent
import gevent.event

from .app.app_main import CLOSE_EVENT
from .app_settings import AppSettings
from .preset.preset import PresetType
from .preset.preset_base import load_presets_from_dir
from .preset.presets_dir import get_user_presets_dir
from .rf2benchmark import RfactorBenchmark
from .rf2command import Command, CommandQueue
from .rf2connect import RfactorState, RfactorConnect
from .rf2events import RfactorLiveEvent, RfactorQuitEvent, RfactorStatusEvent, BenchmarkProgressEvent
from .rfactor import RfactorPlayer
from .utils import capture_app_exceptions


def _restore_pre_replay_preset():
    if AppSettings.replay_playing:
        if AppSettings.replay_preset != '':
            # -- Get currently selected graphics preset
            selected_preset_name = AppSettings.selected_presets.get(str(PresetType.graphics))
            _, selected_preset = load_presets_from_dir(get_user_presets_dir(), PresetType.graphics,
                                                       selected_preset_name=selected_preset_name)

            RfactorStatusEvent.set(f'Applying pre-replay graphics preset: {selected_preset.name}')
            gevent.sleep(1.0)  # If rf2 just quit, give it some time to write settings

            # -- Apply selected preset to rF2
            if selected_preset:
                rf = RfactorPlayer()
                if rf.is_valid:
                    logging.info('Restoring non-replay preset %s', selected_preset_name)
                    rf.write_settings(selected_preset)
        AppSettings.replay_playing = False
        AppSettings.save()


def _rfactor_greenlet_loop():
    # -- Receive Quit rFactor Event from FrontEnd
    if RfactorQuitEvent.event.is_set():
        CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=10.0))
        CommandQueue.append(Command(Command.quit, timeout=10.0))
        # -- Reset Quit Event
        RfactorQuitEvent.reset()

    # -- If we were live before, re-apply previous graphics preset
    if RfactorLiveEvent.changed_from_live():
        _restore_pre_replay_preset()
        gevent.sleep(0.5)

    # -- Update rFactor Live State
    if RfactorConnect.state != RfactorState.unavailable and not RfactorLiveEvent.was_live:
        # -- Report state change to frontend
        RfactorLiveEvent.set(True)

        # -- Get Content
        if CommandQueue.is_empty():
            CommandQueue.append(Command(Command.get_content, timeout=10.0))

        # -- Set Session Settings if present in AppSettings
        if AppSettings.session_selection and len(CommandQueue.queue) < 2:
            CommandQueue.append(Command(Command.set_session_settings, data=AppSettings.session_selection,
                                        timeout=5.0))
            # -- Reset Session Settings
            AppSettings.session_selection = dict()

        # -- Set Content Selection if present in AppSettings
        if AppSettings.content_selected and len(CommandQueue.queue) < 3:
            CommandQueue.append(Command(Command.set_content, data=AppSettings.content_selected, timeout=5.0))
            # -- Reset Content Selection
            AppSettings.content_selected = dict()

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
