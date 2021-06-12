""" Connect to rFactor 2 Ui via it's rest api """
import logging
import time
from typing import Optional, List, Any

import eel
import gevent
import gevent.event

from .app.app_main import CLOSE_EVENT
from .app_settings import AppSettings
from .preset.preset import PresetType
from .preset.preset_base import load_presets_from_dir
from .preset.presets_dir import get_user_presets_dir
from .rf2webui import RfactorState, RfactorConnect
from .rfactor import RfactorPlayer
from .utils import capture_app_exceptions


class Command:
    """ A command to be held in the CommandQueue and to be send to rF2 if it is in the desired state """
    wait_for_state = 0
    play_replay = 1
    switch_fullscreen = 2
    quit = 3
    names = {0: 'wait for state', 1: 'play_replay', 2: 'switch_fullscreen', 3: 'quit'}

    default_timeout = 480.0  # Seconds

    def __init__(self, desired_state: int = None, command: int = None, data: Any = None, timeout: float = None):
        self.desired_state = desired_state
        self.command = command
        self.data = data
        self.timeout = timeout

        self.finished = False
        self.created = time.time()

    def activate(self):
        self.created = time.time()

        logging.debug('rFactor command activated: %s, Desired State: %s, Timeout: %s',
                      Command.names.get(self.command), RfactorState.names.get(self.desired_state), self.timeout)

    def timed_out(self) -> bool:
        result = False
        if (time.time() - self.created) > self.default_timeout:
            result = True
        if self.timeout and ((time.time() - self.created) > self.timeout):
            result = True

        if result:
            logging.info('Rfactor Command timed out: %s', Command.names.get(self.command))

        return result


class CommandQueue:
    """ Queue commands to send to rF2 """
    queue: List[Command] = list()
    current_command: Optional[Command] = None

    @classmethod
    def append(cls, command: Command):
        cls.queue.append(command)

    @classmethod
    def is_empty(cls):
        return len(cls.queue) == 0

    @classmethod
    def _get_next(cls) -> Optional[Command]:
        cls.current_command = None

        if not cls.is_empty():
            cmd = cls.queue.pop(0)
            cmd.activate()
            cls.current_command = cmd
            return cmd

    @classmethod
    def next(cls) -> Optional[Command]:
        if cls.current_command:
            # -- Check current Command for timeout
            if cls.current_command.timed_out():
                return cls._get_next()

            # -- Move to next command in queue if the current command was finished
            if cls.current_command.finished:
                return cls._get_next()
            else:
                return cls.current_command

        return cls._get_next()


class RfactorBaseEvent:
    @classmethod
    def get_nowait(cls) -> Optional[gevent.event.AsyncResult]:
        if hasattr(cls, 'result'):
            try:
                return cls.result.get_nowait()
            except gevent.Timeout:
                pass

    @classmethod
    def reset(cls):
        if hasattr(cls, 'event') and hasattr(cls, 'result'):
            cls.event.clear()
            cls.result = gevent.event.AsyncResult()


class RfactorLiveEvent(RfactorBaseEvent):
    """ Communicate a rfactor live/running event from the rfactor greenlet to the frontend """
    event = gevent.event.Event()
    result = gevent.event.AsyncResult()
    was_live = False

    @classmethod
    def set(cls, value):
        cls.result.set(value)

        if value:
            cls.was_live = True

        # -- Only report state changes
        if RfactorConnect.last_rfactor_live_state != value:
            RfactorConnect.last_rfactor_live_state = value
            cls.event.set()

    @classmethod
    def changed_from_live(cls) -> bool:
        if cls.was_live and (RfactorConnect.state == RfactorState.unavailable):
            cls.was_live = False
            return True
        return False


class RfactorQuitEvent(RfactorBaseEvent):
    """ Communicate a rfactor quit request event from the frontend to the rfactor greenlet """
    event = gevent.event.Event()
    result = gevent.event.AsyncResult()
    quit_result = gevent.event.AsyncResult()

    @classmethod
    def set(cls, value):
        cls.result.set(value)
        cls.event.set()
        # -- Reset async result
        cls.quit_result = gevent.event.AsyncResult()


class RfactorStatusEvent(RfactorBaseEvent):
    """ post status updates to the FrontEnd """
    event = gevent.event.Event()
    result = gevent.event.AsyncResult()
    empty = True

    @classmethod
    def set(cls, value):
        if value:
            cls.empty = False
        else:
            cls.empty = True
        cls.result.set(value)
        cls.event.set()


class ReplayPlayEvent(RfactorBaseEvent):
    """ Communicate a replay play request to rfactor event loop """
    event = gevent.event.Event()
    result = gevent.event.AsyncResult()
    is_playing_replay = False

    @classmethod
    def set(cls, value):
        cls.result.set(value)
        cls.event.set()


def _create_replay_commands(replay_name: str):
    # 1. Wait for UI
    CommandQueue.append(Command(RfactorState.ready, Command.wait_for_state, timeout=120.0))
    # 2. Load Replay
    CommandQueue.append(Command(RfactorState.ready, Command.play_replay, replay_name, timeout=60.0))
    # 3. Wait UI Loading State
    CommandQueue.append(Command(RfactorState.loading, Command.wait_for_state, timeout=90.0))
    # 4. Wait UI Ready State
    CommandQueue.append(Command(RfactorState.ready, Command.wait_for_state, timeout=800.0))
    # 5. Switch FullScreen
    CommandQueue.append(Command(RfactorState.ready, Command.switch_fullscreen, timeout=60.0))


def _play_replay(replay_name: str) -> bool:
    is_playing_replay = False

    if not replay_name:
        logging.error('Can not play replay without name!')
        return False

    # RfactorConnect.wait_for_rf2_ui(20.0)
    replays = RfactorConnect.get_replays()
    gevent.sleep(0.1)

    for r in replays:
        if r.get('replayName', '') == replay_name:
            logging.debug('Matched Web UI replay with requested replay id: %s', r.get('id'))
            RfactorConnect.play_replay(r.get('id', 0))
            is_playing_replay = True
            break

    if not is_playing_replay:
        return False
    return True


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
        CommandQueue.append(Command(RfactorState.ready, Command.wait_for_state, timeout=60.0))
        CommandQueue.append(Command(RfactorState.ready, Command.quit, timeout=30.0))
        # -- Reset Quit Event
        RfactorQuitEvent.reset()

    # -- Receive Replay Play Event from FrontEnd
    if ReplayPlayEvent.event.is_set():
        replay_name = ReplayPlayEvent.get_nowait()
        ReplayPlayEvent.reset()
        _create_replay_commands(replay_name)

    # -- Update rFactor Live State
    if RfactorConnect.state != RfactorState.unavailable:
        # -- Report state change to frontend
        RfactorLiveEvent.set(True)
    else:
        # -- Report state change to frontend
        RfactorLiveEvent.set(False)

    # -- If we were live before, re-apply previous graphics preset
    if RfactorLiveEvent.changed_from_live():
        _restore_pre_replay_preset()

    # ---------------------------
    # -- COMMAND QUEUE
    # ---------------------------
    command = CommandQueue.next()
    if not command:
        # -- Reset rF2 FrontEnd status message
        if not RfactorStatusEvent.empty:
            RfactorStatusEvent.set('')
        RfactorConnect.set_to_idle_timeout()

        # -- Call the check connection method every loop
        #    - it will only actually check in it's own time intervals
        #    - will not track loading state if shared memory available
        RfactorConnect.check_connection(require_loading_state=False)
        return

    # -- We have active commands, alter Connection checks accordingly
    # -- Track State changes more frequently
    RfactorConnect.set_to_active_timeout()
    # -- Require to track loading state when checking connection
    RfactorConnect.check_connection(require_loading_state=True)

    if command.command == Command.wait_for_state:
        # -- Wait for state
        if command.desired_state == RfactorConnect.state:
            logging.debug('Found desired command state: %s', RfactorState.names.get(command.desired_state))
            command.finished = True
        RfactorStatusEvent.set(f'Waiting for rF2 state: {RfactorState.names.get(command.desired_state)}')
    elif command.command == Command.play_replay:
        # -- Play Replay
        if _play_replay(command.data):
            logging.debug('Playing rF2 replay: %s', command.data)
            AppSettings.replay_playing = True
            AppSettings.save()
            RfactorLiveEvent.set(True)
            RfactorStatusEvent.set(f'Loading Replay {command.data}')
            command.finished = True
    elif command.command == Command.switch_fullscreen:
        # -- Switch Event Monitor to FullScreen
        logging.debug('Switching rF replay to fullscreen.')
        RfactorStatusEvent.set(f'Switching rF2 Monitor to fullscreen mode.')
        if RfactorConnect.switch_event_monitor_fullscreen():
            command.finished = True
    elif command.command == Command.quit:
        # -- Quit rF2
        logging.debug('Executing command quit rF2.')
        RfactorStatusEvent.set('Sending quit event to WebUI')
        quit_result = RfactorConnect.quit()
        RfactorQuitEvent.quit_result.set(quit_result)

        if quit_result:
            command.finished = True


@capture_app_exceptions
def rfactor_greenlet():
    logging.info('rFactor Greenlet started.')
    RfactorConnect.start_request_thread()

    while True:
        _rfactor_greenlet_loop()

        close = CLOSE_EVENT.wait(timeout=3.0)
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
            logging.debug('Updating rf2 status message: %s', status)
            eel.rfactor_status(status)

        RfactorStatusEvent.reset()
