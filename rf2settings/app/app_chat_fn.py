import json
import logging
from multiprocessing import shared_memory

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


@capture_app_exceptions
def post_chat_message(message):
    if not message:
        return

    logging.debug('Posting chat message: %s', message)

    # open shared memory
    try:
        shm = shared_memory.SharedMemory("rF2_ChatTransceiver_SM", create=False)
    except FileNotFoundError:
        return

    destination = 0  # message center

    # make sure message does not exceed message size
    mem_bytes = f'{destination}{message[:128]}'.encode('cp1252')

    # write to shared memory
    shm.buf[:len(mem_bytes)] = mem_bytes
    logging.debug('Writing to shared memory: %s', mem_bytes)

    shm.close()
