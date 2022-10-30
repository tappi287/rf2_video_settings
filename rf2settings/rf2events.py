from typing import Optional

import gevent
import gevent.event

from .rf2connect import RfactorState, RfactorConnect


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


class RfactorYouTubeEvent(RfactorBaseEvent):
    """ post status updates to the FrontEnd """
    event = gevent.event.Event()
    result = gevent.event.AsyncResult()
    is_active = False

    @classmethod
    def set(cls, value):
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


class StartBenchmarkEvent(RfactorBaseEvent):
    event = gevent.event.Event()
    result = gevent.event.AsyncResult()

    @classmethod
    def set(cls, value):
        cls.result.set(value)
        cls.event.set()


class RecordBenchmarkEvent(RfactorBaseEvent):
    event = gevent.event.Event()
    result = gevent.event.AsyncResult()

    @classmethod
    def set(cls, value):
        cls.result.set(value)
        cls.event.set()


class BenchmarkProgressEvent(RfactorBaseEvent):
    event = gevent.event.Event()
    result = gevent.event.AsyncResult()

    @classmethod
    def set(cls, value):
        cls.result.set(value)
        cls.event.set()
