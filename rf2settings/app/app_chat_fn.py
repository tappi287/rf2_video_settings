import json
import logging

from ..app_settings import AppSettings
from ..utils import capture_app_exceptions


@capture_app_exceptions
def save_chat_settings(settings):
    logging.info('Received Chat Settings: %s', settings)
    AppSettings.chat_settings = settings
    AppSettings.save()

    return json.dumps({'result': True, })


@capture_app_exceptions
def get_chat_settings():
    logging.info('Providing chat settings: %s', AppSettings.chat_settings)
    return json.dumps({'result': True, 'settings': AppSettings.chat_settings})
