import logging
from typing import Optional, Union

from googleapiclient.discovery import build

from rf2settings.app_settings import AppSettings

LAST_ERRORS = list()
API_K = AppSettings.chat_plugin_version.get("2022.10.19")


def get_channel_id_by_username(username: str) -> Optional[str]:
    youtube = build('youtube', 'v3', developerKey=API_K, static_discovery=False)

    request = youtube.channels().list(part='id', forUsername=username)
    response: dict = request.execute()
    if not response or not response.get('items'):
        logging.debug(f'YouTube username {username} not found.')
        return

    channel = response.get('items', [dict()])[0]
    channel_id = channel.get('id')
    if not channel_id:
        logging.debug(f'YouTube channel id for username {username} not found.')
        return

    logging.debug(f'Found Channel ID {channel_id} for Username: {username}')
    return channel_id


def get_live_stream_by_channel_id(channel_id) -> Optional[dict]:
    youtube = build('youtube', 'v3', developerKey=API_K, static_discovery=False)

    # -- Get Live Broadcast Video ID
    request = youtube.search().list(
        part='snippet', channelId=channel_id, eventType="live", type="video"
    )
    response: dict = request.execute()
    if not response or not response.get('items'):
        return

    video_id = response.get('items')[0].get('id', dict()).get('videoId')
    title = response.get('items')[0].get('snippet', dict()).get('title')

    # -- Get Video live-streaming details
    request = youtube.videos().list(
        part="liveStreamingDetails", id=video_id
    )
    response: dict = request.execute()
    if not response or not response.get('items'):
        return

    # -- Get live chat id
    live_chat_id = response.get('items')[0].get('liveStreamingDetails', dict()).get('activeLiveChatId')
    if not live_chat_id:
        return

    # -- Form live stream result
    live_stream = response.get('items')[0]
    live_stream['snippet'] = dict()
    live_stream['snippet']['liveChatId'] = live_chat_id
    live_stream['snippet']['title'] = title
    return live_stream


def get_chat_messages(credentials=None, live_stream: dict = None) -> Union[bool, list]:
    messages = list()
    live_chat_id = live_stream.get("snippet", dict()).get("liveChatId")
    if not live_chat_id:
        return messages

    if credentials:
        youtube = build('youtube', 'v3', credentials=credentials, static_discovery=False)
    else:
        youtube = build('youtube', 'v3', developerKey=API_K, static_discovery=False)

    request = youtube.liveChatMessages().list(liveChatId=live_chat_id, part="id,snippet,authorDetails", maxResults=10)
    response: dict = request.execute()

    # -- Handle errors
    if response.get("error") and response.get("error", dict()).get("errors"):
        logging.error(response)
        quota_exceeded = False
        for err in response.get("error", dict()).get("errors"):
            global LAST_ERRORS
            LAST_ERRORS.append(err)

            if err.get("reason") == "quotaExceeded":
                quota_exceeded = True

        if quota_exceeded:
            return False

    if not response or not response.get('items'):
        return messages

    # -- Create messages list
    for item in response.get('items'):
        message = item.get('snippet').get('displayMessage')
        display_name = item.get('authorDetails').get('displayName')
        messages.append(f'{display_name}: {message}')
    return messages


def get_last_errors():
    global LAST_ERRORS
    errors = LAST_ERRORS[:]
    LAST_ERRORS = list()
    return errors
