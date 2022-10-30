import logging

import eel
import gevent

from rf2settings.app.app_main import CLOSE_EVENT
from rf2settings.app_settings import AppSettings
from rf2settings.chat.youtube import get_chat_messages
from rf2settings.rf2events import RfactorYouTubeEvent
from rf2settings.utils import capture_app_exceptions

CURRENT_YT_MESSAGES = list()
POLLING_TIMEOUT = 35.0


def _yt_greenlet_loop():
    # -- Check if YouTube live chat is active
    if not RfactorYouTubeEvent.is_active or AppSettings.yt_livestream is None:
        return

    # -- Get new messages
    global CURRENT_YT_MESSAGES
    messages = get_chat_messages(AppSettings.yt_credentials, AppSettings.yt_livestream)

    # -- Quota exceeded!
    if messages is False:
        AppSettings.yt_livestream = None
        RfactorYouTubeEvent.is_active = False
        return

    # -- No new messages
    if messages == CURRENT_YT_MESSAGES:
        gevent.sleep(POLLING_TIMEOUT)
        return

    # -- New messages
    new_messages = list()
    for message in messages:
        if message in CURRENT_YT_MESSAGES:
            continue
        new_messages.append(message)

    CURRENT_YT_MESSAGES = messages
    logging.debug('Setting new YouTube messages: %s', new_messages)
    RfactorYouTubeEvent.set(new_messages)
    gevent.sleep(POLLING_TIMEOUT)


def youtube_eventloop():
    if RfactorYouTubeEvent.event.is_set():
        messages = RfactorYouTubeEvent.get_nowait()
        if messages:
            eel.youtube_messages(messages)
        RfactorYouTubeEvent.reset()


@capture_app_exceptions
def youtube_greenlet():
    while True:
        _yt_greenlet_loop()

        close = CLOSE_EVENT.wait(timeout=5.0)
        if close:
            logging.info('YouTube greenlet received CLOSE event.')
            break
    logging.info('YouTube greenlet exiting.')
