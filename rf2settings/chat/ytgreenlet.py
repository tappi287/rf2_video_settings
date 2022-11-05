import logging

import eel
import gevent

from rf2settings.app.app_main import CLOSE_EVENT
from rf2settings.app_settings import AppSettings
from rf2settings.chat import youtube
from rf2settings.rf2events import RfactorYouTubeEvent, RfactorYouTubeErrorEvent, RfactorYouTubeLiveEvent
from rf2settings.rf2events import RfactorYouTubeSetUsernameEvent
from rf2settings.utils import capture_app_exceptions

CURRENT_YT_USERNAME = str()
CURRENT_YT_MESSAGES = list()
POLLING_TIMEOUT = 35.0


def _yt_greenlet_loop():
    # -- Get Username set by front end
    global CURRENT_YT_USERNAME
    if RfactorYouTubeSetUsernameEvent.event.is_set():
        new_user_name = RfactorYouTubeSetUsernameEvent.get_nowait()
        RfactorYouTubeSetUsernameEvent.reset()

        if new_user_name != CURRENT_YT_USERNAME:
            AppSettings.yt_livestream = None
        CURRENT_YT_USERNAME = new_user_name

    # -- Check if YouTube live chat should be active
    if not RfactorYouTubeEvent.is_active:
        return

    # -- Check if we know of an active broadcast
    if AppSettings.yt_livestream is None:
        try:
            if AppSettings.yt_channel_id.get(CURRENT_YT_USERNAME, None) is None:
                channel_id = youtube.get_channel_id_by_username(CURRENT_YT_USERNAME)
                if channel_id:
                    AppSettings.yt_channel_id[CURRENT_YT_USERNAME] = channel_id
            else:
                channel_id = AppSettings.yt_channel_id.get(CURRENT_YT_USERNAME)

            AppSettings.yt_livestream = youtube.get_live_stream_by_channel_id(channel_id)
        except Exception as e:
            error = f'Error acquiring YouTube Live Stream data: {e}'
            RfactorYouTubeErrorEvent.set([error])
            AppSettings.yt_livestream = None

        if AppSettings.yt_livestream is None:
            RfactorYouTubeLiveEvent.set("")
            logging.debug('No active YouTube Broadcast found.')
            gevent.sleep(POLLING_TIMEOUT * 10.0)
            return
        else:
            RfactorYouTubeLiveEvent.set(
                AppSettings.yt_livestream.get("snippet", dict()).get("title")
            )

    # -- Get new messages
    global CURRENT_YT_MESSAGES
    try:
        messages = youtube.get_chat_messages(live_stream=AppSettings.yt_livestream)
    except Exception as e:
        error = f'Error acquiring YouTube live chat messages: {e}'
        RfactorYouTubeErrorEvent.set([error])
        gevent.sleep(POLLING_TIMEOUT)
        return

    # -- Error receiving messages
    if messages is False:
        AppSettings.yt_livestream = None
        RfactorYouTubeErrorEvent.set(youtube.get_last_errors())
        return

    # -- No new messages
    if messages == CURRENT_YT_MESSAGES or len(messages) == 0:
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

        if CLOSE_EVENT.is_set():
            logging.info('YouTube greenlet received CLOSE event.')
            break
        gevent.sleep(5.0)

    logging.info('YouTube greenlet exiting.')
