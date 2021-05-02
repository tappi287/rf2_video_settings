""" Connect to rFactor 2 Ui via it's rest api """
import logging
import time
from queue import Queue, Empty
from threading import Thread, Event
from typing import Optional, Union, List, Any

import eel
import gevent
import gevent.event

from urllib.error import URLError
from . import requests
from .app.app_main import CLOSE_EVENT
from .app_settings import AppSettings
from .preset.preset import PresetType
from .preset.preset_base import load_presets_from_dir
from .preset.presets_dir import get_user_presets_dir
from .rfactor import RfactorPlayer
from .utils import AppExceptionHook, capture_app_exceptions


class RfactorState:
    unavailable = 0
    loading = 1
    ready = 2

    names = {0: 'Unavailable', 1: 'Loading', 2: 'Ready'}


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


class RfactorConnect:
    host = 'localhost'
    web_ui_port: int = 0  # Call update_web_ui_port to update the port from current player.json
    state = 0  # RfactorState
    get_request_time = 0.5  # float seconds timeout for get requests

    long_timeout = 120.0    # Maximum connection check timeout
    idle_timeout = 20.0     # Start with this time out after an active connection
    active_timeout = 2.0    # Check connection timeout while eg. loading
    memory_timeout = 5.0   # Shorter idle timeout if state can be checked with shared memory

    last_connection_check = time.time()
    connection_check_interval = idle_timeout  # Revalidate connection every float seconds

    # -- Track rF2 available state changes
    last_rfactor_live_state = False

    # -- Shared memory available
    #    set from outside if rf2sharedmemory is available
    #    connection checks will be more efficient
    use_shared_memory = False
    shared_mem_check_method = None
    last_shared_mem_state = False

    # -- Threaded requests
    request_queue = Queue()
    response_queue = Queue()
    close_event = Event()
    request_thread: Optional[Thread] = None

    @staticmethod
    def _request_thread_loop(request_queue: Queue, response_queue: Queue, close_event: Event):
        logging.debug('RfactorConnect request thread started.')

        while not close_event.is_set():
            # -- Check for requests
            try:
                r = request_queue.get(timeout=1.0)
            except Empty:
                continue

            # -- Fulfill request
            if r.get('method') == 'GET':
                try:
                    response = RfactorConnect._get_request(r.get('url'))
                except Exception as e:
                    logging.error('Error during GET request: %s', e)
                    continue

                logging.debug('Request Thread received response for GET request to %s', r.get('url'))
                response_queue.put(response or False)  # Make sure we do not put None in the queue
            elif r.get('method') == 'POST':
                try:
                    response = RfactorConnect._post_request(r.get('url'), r.get('data'))
                except Exception as e:
                    logging.error('Error during POST request: %s', e)
                    continue

                logging.debug('Request Thread received response for POST request to %s', r.get('url'))
                response_queue.put(response or False)  # Make sure we do not put None in the queue

        logging.debug('RfactorConnect request thread exiting.')

    @classmethod
    def _check_response(cls) -> Optional[dict]:
        response = None
        # Make sure to collect all responses
        while cls.response_queue.qsize() > 0:
            try:
                response = cls.response_queue.get_nowait()
            except Empty:
                break
        return response

    @classmethod
    def start_request_thread(cls):
        cls.request_thread = Thread(target=cls._request_thread_loop,
                                    args=(cls.request_queue, cls.response_queue, cls.close_event))
        cls.request_thread.start()

    @classmethod
    def stop_request_thread(cls) -> None:
        logging.debug('Stopping RfactorConnect request thread.')
        cls.close_event.set()
        if cls.request_thread.is_alive():
            logging.debug('Joining RfactorConnect request thread.')
            cls.request_thread.join(timeout=5.0)
            logging.debug('RfactorConnect request thread joined.')

    @classmethod
    def base_url(cls) -> str:
        return f'http://{cls.host}:{cls.web_ui_port}'

    @classmethod
    def setup_shared_memory(cls, shared_memory_method: callable):
        logging.debug('Setting up RfactorConnect shared memory usage.')
        cls.use_shared_memory = True
        cls.shared_mem_check_method = shared_memory_method

    @classmethod
    def check_connection(cls, require_loading_state: bool = False) -> None:
        """ Check if Web UI connection is available every timeout interval
            or use shared memory if reported to be available.

        :param require_loading_state: if running/not running state is not sufficient info
        :return:
        """
        response = cls._check_response()
        if response is not None:
            cls.set_state(response)
            return

        # - Only check every connection_check_interval
        timeout = min(cls.memory_timeout if cls.use_shared_memory else cls.long_timeout, cls.connection_check_interval)
        if time.time() - cls.last_connection_check < timeout:
            return

        # -- Increase timeout with every check
        if cls.connection_check_interval < cls.long_timeout:
            cls.connection_check_interval = cls.connection_check_interval * 1.1

        # -- Update state based on shared memory
        if cls.use_shared_memory and not require_loading_state:
            try:
                cls.set_state_from_shared_memory(cls.shared_mem_check_method())
                return
            except Exception as e:
                logging.error('Error checking shared memory: %s', e)

        # -- Find WebUI port if not already known
        if cls.web_ui_port == 0:
            if not cls.update_web_ui_port():
                return

        # -- Check navigation state in http request thread
        if cls.request_queue.empty():
            logging.debug('Checking for rFactor 2 http connection. Interval: %.2f', timeout)
            cls.last_connection_check = time.time()  # Update TimeOut
            cls.request_queue.put({'method': 'GET', 'url': '/navigation/state'})

    @classmethod
    def set_state(cls, nav_state: Union[bool, dict]) -> None:
        previous_state = int(cls.state)

        if isinstance(nav_state, dict):
            if nav_state.get('status_code', 200) != 200:
                # -- Assume loading state if we received a request with a non 200 status
                cls.state = RfactorState.loading
            else:
                # -- Set State loading or ready
                cls.state = RfactorState.loading if nav_state.get('loadingStatus', dict()
                                                                  ).get('loading') else RfactorState.ready
        elif nav_state is False:
            # -- Set unavailable
            cls.state = RfactorState.unavailable

        if previous_state != cls.state:
            if cls.state == RfactorState.loading:
                cls.set_to_active_timeout()
            elif cls.state == RfactorState.unavailable:
                cls.set_to_idle_timeout()
            logging.debug('Updating rFactor 2 state to: %s', RfactorState.names.get(cls.state))

    @classmethod
    def set_state_from_shared_memory(cls, shared_memory_state: bool):
        # -- If shared memory is available
        #    set state based on shared memory state
        if cls.last_shared_mem_state != shared_memory_state:
            logging.debug('Updating RfactorConnect shared memory state: %s',
                          'Available' if shared_memory_state else 'Unavailable')
            cls.last_shared_mem_state = shared_memory_state

            if shared_memory_state:
                # -- Set to ready state
                cls.set_state(dict(loadingStatus=dict(loading=False)))
            else:
                # -- Set to unavailable state
                cls.set_state(False)

    @classmethod
    def get_replays(cls) -> list:
        """ Request all replays from the rFactor 2 UI """
        cls.wait_for_rf2_ui(5.0)
        if cls.state != RfactorState.ready:
            return list()

        return cls._get_request('/rest/watch/replays') or list()

    @classmethod
    def play_replay(cls, replay_id: int) -> bool:
        """ Request rFactor 2 to play the replay with the provided id """
        cls.wait_for_rf2_ui(5.0)
        if cls.state != RfactorState.ready:
            return False

        return True if cls._get_request(f'/rest/watch/play/{replay_id}') else False

    @classmethod
    def switch_event_monitor_fullscreen(cls) -> bool:
        """ Request the Web UI to switch the Event Monitor to FullScreen """
        return True if cls._post_request('/navigation/action/NAV_TO_FULL_EVENT_MONITOR', None) else False

    @classmethod
    def quit(cls) -> bool:
        """ Requests rFactor 2 to quit """
        cls.wait_for_rf2_ui(5.0)
        if cls.state != RfactorState.ready:
            return False

        r = cls._post_request('/rest/start/quitGame')
        cls.set_state_from_shared_memory(False)
        if not r:
            return False
        return True if r.status_code == 204 else False

    @classmethod
    def set_to_active_timeout(cls):
        """ Track state changes more frequently """
        if cls.connection_check_interval > cls.active_timeout:
            cls.connection_check_interval = cls.active_timeout

    @classmethod
    def set_to_idle_timeout(cls):
        """ Track state changes in idle """
        if cls.connection_check_interval < cls.idle_timeout:
            cls.connection_check_interval = cls.idle_timeout

    @classmethod
    def wait_for_rf2_ui(cls, timeout_secs: float, wait_for_state_change: bool = False):
        """ Wait for a rFactor 2 Web UI connection in ready state """
        start_time = time.time()
        previous_state = int(cls.state)
        cls.set_to_active_timeout()

        while not time.time() - start_time > timeout_secs:
            cls.check_connection(require_loading_state=True)
            if wait_for_state_change and cls.state != previous_state:
                wait_for_state_change = False
            if cls.state == RfactorState.ready and not wait_for_state_change:
                return
            gevent.sleep(0.5)

        logging.info('Waiting for active rF Web UI timed out.')

    @classmethod
    def _get_request(cls, url) -> Optional[dict]:
        try:
            r = requests.get(f'{cls.base_url()}{url}', timeout=cls.get_request_time)
        except URLError:
            return

        if r.status_code != 200:
            logging.info('Response for request to %s was %s %s', url, r.status_code, r.text)
            return {'status_code': r.status_code}

        return r.json()

    @classmethod
    def _post_request(cls, url, data=None) -> Optional[requests.RequestResponse]:
        try:
            r = requests.post(f'{cls.base_url()}{url}', data=data)
        except Exception as exc:
            logging.error('Could not connect to rFactor 2 Web UI: %s', exc)
            return

        logging.info('Response for POST request to %s was %s %s', url, r.status_code, r.text)
        return r

    @staticmethod
    def update_web_ui_port() -> bool:
        rf = RfactorPlayer()
        if rf.is_valid:
            if hasattr(rf.options, 'misc_options'):
                o = rf.options.misc_options.get_option('WebUI port')
                RfactorConnect.web_ui_port = o.value
                logging.debug('Updated RfactorConnect Web UI port to: %s', RfactorConnect.web_ui_port)
                return True
        return False


class RfactorLiveEvent:
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


class RfactorQuitEvent:
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

    @classmethod
    def reset(cls):
        cls.event.clear()
        cls.result = gevent.event.AsyncResult()


class RfactorStatusEvent:
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

    @classmethod
    def reset(cls):
        cls.event.clear()
        cls.result = gevent.event.AsyncResult()


class ReplayPlayEvent:
    """ Communicate a replay play request to rfactor event loop """
    event = gevent.event.Event()
    result = gevent.event.AsyncResult()
    is_playing_replay = False

    @classmethod
    def set(cls, value):
        cls.result.set(value)
        cls.event.set()

    @classmethod
    def reset(cls):
        cls.event.clear()
        cls.result = gevent.event.AsyncResult()


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
        try:
            replay_name = ReplayPlayEvent.result.get_nowait()
        except gevent.Timeout:
            replay_name = None
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
        try:
            is_live = RfactorLiveEvent.result.get_nowait()
        except gevent.Timeout:
            is_live = None

        # -- Update rFactor live state to front end
        if is_live is not None:
            eel.rfactor_live(is_live)

    if RfactorStatusEvent.event.is_set():
        try:
            status = RfactorStatusEvent.result.get_nowait()
        except gevent.Timeout:
            status = False

        if status is not False:
            logging.debug('Updating rf2 status message: %s', status)
            eel.rfactor_status(status)

        RfactorStatusEvent.reset()
