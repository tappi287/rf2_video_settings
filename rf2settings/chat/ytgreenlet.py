import logging

import eel

from rf2settings.app.app_main import CLOSE_EVENT
from rf2settings.app_settings import AppSettings
from rf2settings.chat.youtube import get_live_stream, get_chat_messages, get_last_errors
from rf2settings.rf2events import RfactorYouTubeEvent, RfactorYouTubeErrorEvent, RfactorYouTubeLiveEvent
from rf2settings.utils import capture_app_exceptions

CURRENT_YT_MESSAGES = list()
POLLING_TIMEOUT = 35.0


def _yt_greenlet_loop():
    # -- Check if YouTube live chat should be active
    if not RfactorYouTubeEvent.is_active:
        return

    # -- Check if we know of an active broadcast
    if AppSettings.yt_livestream is None:
        try:
            AppSettings.yt_livestream = get_live_stream(AppSettings.yt_credentials)
        except Exception as e:
            error = f'Error acquiring YouTube Live Stream data: {e}'
            RfactorYouTubeErrorEvent.set([error])
            AppSettings.yt_livestream = None

        if AppSettings.yt_livestream is None:
            RfactorYouTubeLiveEvent.set("")
            logging.debug('No active YouTube Broadcast found.')
            CLOSE_EVENT.wait(POLLING_TIMEOUT * 10)
            return
        else:
            RfactorYouTubeLiveEvent.set(
                AppSettings.yt_livestream.get("snippet", dict()).get("title")
            )

    # -- Get new messages
    global CURRENT_YT_MESSAGES
    try:
        messages = get_chat_messages(AppSettings.yt_credentials, AppSettings.yt_livestream)
    except Exception as e:
        error = f'Error acquiring YouTube live chat messages: {e}'
        RfactorYouTubeErrorEvent.set([error])
        CLOSE_EVENT.wait(POLLING_TIMEOUT)
        return

    # -- Quota exceeded!
    if messages is False:
        AppSettings.yt_livestream = None
        RfactorYouTubeEvent.is_active = False
        RfactorYouTubeErrorEvent.set(get_last_errors())
        return

    # -- No new messages
    if messages == CURRENT_YT_MESSAGES or len(messages) == 0:
        CLOSE_EVENT.wait(POLLING_TIMEOUT)
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
    CLOSE_EVENT.wait(POLLING_TIMEOUT)


def youtube_eventloop():
    if RfactorYouTubeEvent.event.is_set():
        messages = RfactorYouTubeEvent.get_nowait()
        if messages:
            eel.youtube_messages(messages)
        RfactorYouTubeEvent.reset()

    if RfactorYouTubeErrorEvent.event.is_set():
        errors = RfactorYouTubeErrorEvent.get_nowait()
        if errors:
            eel.youtube_errors(errors)
        RfactorYouTubeErrorEvent.reset()

    if RfactorYouTubeLiveEvent.event.is_set():
        broadcast_title = RfactorYouTubeLiveEvent.get_nowait()
        eel.youtube_live(broadcast_title)
        RfactorYouTubeLiveEvent.reset()


@capture_app_exceptions
def youtube_greenlet():
    while True:
        _yt_greenlet_loop()

        close = CLOSE_EVENT.wait(timeout=5.0)
        if close:
            logging.info('YouTube greenlet received CLOSE event.')
            break
    logging.info('YouTube greenlet exiting.')
