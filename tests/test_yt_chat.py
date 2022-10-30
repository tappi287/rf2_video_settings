import logging

from rf2settings.chat.youtube import get_oauth_credentials, get_live_stream, get_chat_messages


def test_yt_chat():
    credentials = get_oauth_credentials()
    if not credentials:
        return
    live_stream = get_live_stream(credentials)
    messages = get_chat_messages(credentials, live_stream)
    logging.debug(messages)
