import json
import logging
from pathlib import Path
from typing import Optional, Union
from zipfile import ZipFile

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from rf2settings.globals import get_settings_dir, get_data_dir


LAST_ERRORS = list()


def remove_oauth_credentials():
    credentials_path = get_settings_dir() / 'ydata.zip'
    if credentials_path.exists() and credentials_path.is_file():
        credentials_path.unlink()


def load_oauth_credentials() -> Optional[Credentials]:
    # -- Load
    credentials_path = get_settings_dir() / 'ydata.zip'
    if credentials_path.exists() and credentials_path.is_file():
        with ZipFile(credentials_path, 'r') as zip_file:
            cred_json = zip_file.read('c.json')

        credentials = Credentials.from_authorized_user_info(json.loads(cred_json))
        logging.debug('Loaded Credentials for: %s', credentials.client_id)
        return credentials


def acquire_oauth_credentials() -> Optional[Credentials]:
    # -- Acquire new with user interacting with browser
    client_file = Path(get_settings_dir()).joinpath('client.json')
    flow = InstalledAppFlow.from_client_secrets_file(
        client_file.as_posix(),
        scopes=['https://www.googleapis.com/auth/youtube.readonly']
    )
    credentials: Credentials = flow.run_local_server(port=8080, prompt="consent", timeout_seconds=60)

    # -- Save
    if credentials and isinstance(credentials, Credentials):
        credentials_path = get_settings_dir() / 'ydata.zip'

        with ZipFile(credentials_path, 'w') as zip_file:
            zip_file.writestr('c.json', credentials.to_json())
        logging.debug('Saved Credentials for: %s', credentials.client_id)
        return credentials


def get_live_stream(credentials) -> Optional[dict]:
    if not credentials:
        return

    youtube = build('youtube', 'v3', credentials=credentials, static_discovery=False)

    request = youtube.liveBroadcasts().list(
        part="snippet,contentDetails,status",
        broadcastStatus="active",
        broadcastType="all"
    )

    response: dict = request.execute()
    if not response or not response.get('items'):
        return

    live_stream = response.get('items', [dict()])[0]
    if not live_stream:
        return

    logging.debug(f'Found Live Stream with ID {live_stream.get("id")} with live chat id '
                  f'{live_stream.get("snippet", dict()).get("liveChatId")}')

    return live_stream


def get_chat_messages(credentials, live_stream: dict) -> Union[bool, list]:
    messages = list()
    live_chat_id = live_stream.get("snippet", dict()).get("liveChatId")
    if not live_chat_id or not credentials:
        return messages

    youtube = build('youtube', 'v3', credentials=credentials, static_discovery=False)
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
