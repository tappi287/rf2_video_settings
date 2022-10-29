import json
import logging
from pathlib import Path
from typing import Optional, Tuple
from zipfile import ZipFile

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from rf2settings.app_settings import AppSettings
from rf2settings.globals import get_current_modules_dir, get_settings_dir, get_data_dir
from rf2settings.log import setup_logging


def remove_oauth_credentials():
    AppSettings.yt_credentials = None
    credentials_path = get_settings_dir() / 'ydata.zip'
    if credentials_path.exists() and credentials_path.is_file():
        credentials_path.unlink()


def get_oauth_credentials() -> Optional[Credentials]:
    # -- Cache
    if AppSettings.yt_credentials is not None:
        return AppSettings.yt_credentials

    # -- Load
    credentials_path = get_settings_dir() / 'ydata.zip'
    if credentials_path.exists() and credentials_path.is_file():
        with ZipFile(credentials_path, 'r') as zip_file:
            cred_json = zip_file.read('c.json')

        credentials = Credentials.from_authorized_user_info(json.loads(cred_json))
        AppSettings.yt_credentials = credentials
        logging.debug('Loaded Credentials for: %s', credentials.client_id)
        return credentials

    # -- Acquire new with user interacting with browser
    client_secrets_file = Path(get_data_dir()).joinpath('client_secret.json')
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file.as_posix(),
        scopes=['https://www.googleapis.com/auth/youtube.readonly']
    )
    credentials: Credentials = flow.run_local_server(port=8080, prompt="consent", timeout_seconds=60)

    # -- Save
    if credentials:
        with ZipFile(credentials_path, 'w') as zip_file:
            zip_file.writestr('c.json', credentials.to_json())
        AppSettings.yt_credentials = credentials
        logging.debug('Saved Credentials for: %s', credentials.client_id)
        return credentials


def get_live_stream(credentials) -> Optional[dict]:
    youtube = build('youtube', 'v3', credentials=credentials)

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


def get_chat_messages(credentials, live_stream: dict) -> list:
    messages = list()
    live_chat_id = live_stream.get("snippet", dict()).get("liveChatId")
    if not live_chat_id:
        return messages

    youtube = build('youtube', 'v3', credentials=credentials)
    request = youtube.liveChatMessages().list(liveChatId=live_chat_id, part="id,snippet,authorDetails", maxResults=10)
    response: dict = request.execute()
    if not response or not response.get('items'):
        return messages

    # -- Create messages list
    for item in response.get('items'):
        message = item.get('snippet').get('displayMessage')
        display_name = item.get('authorDetails').get('displayName')
        messages.append(f'{display_name}: {message}')
    return messages


def test_yt_chat():
    credentials = get_oauth_credentials()
    if not credentials:
        return
    live_stream = get_live_stream(credentials)
    messages = get_chat_messages(credentials, live_stream)
    logging.debug(messages)


if __name__ == '__main__':
    setup_logging(__name__)
    test_yt_chat()
