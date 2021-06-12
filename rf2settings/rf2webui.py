import logging
import time
from queue import Queue, Empty
from threading import Event, Thread
from typing import Optional, Union
from urllib.error import URLError

import gevent

from rf2settings import requests
from rf2settings.rfactor import RfactorPlayer


class RfactorState:
    unavailable = 0
    loading = 1
    ready = 2

    names = {0: 'Unavailable', 1: 'Loading', 2: 'Ready'}


class RfactorConnect:
    """ Helper class to connect to a running rF2 instance WebUi and request current rF2 state and call
        WebUi endpoints to control the running instance.
    """
    host = 'localhost'
    web_ui_port: int = 0  # Call update_web_ui_port to update the port from current player.json
    state = 0  # RfactorState
    get_request_time = 0.5  # float seconds timeout for get requests

    long_timeout = 120.0    # Maximum connection check timeout
    idle_timeout = 20.0     # Start with this time out after an active connection
    active_timeout = 2.0    # Check connection timeout while eg. loading
    memory_timeout = 5.0    # Shorter idle timeout if state can be checked with shared memory

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