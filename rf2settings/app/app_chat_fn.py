import json
import logging
import shutil
from multiprocessing import shared_memory
from pathlib import Path

from open_vr_mod.util.utils import get_file_hash
from rf2settings.app.app_main_fn import _get_rf_location
from rf2settings.app_settings import AppSettings
from rf2settings.globals import get_data_dir, CHAT_PLUGIN_NAME, RFACTOR_PLUGIN_PATH
from rf2settings.utils import capture_app_exceptions


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


def decode_message(message):
    decoded_message = str()

    for character in message:
        try:
            character.encode('cp1252')
        except UnicodeEncodeError:
            continue
        decoded_message += character
    return decoded_message


@capture_app_exceptions
def post_chat_message(message):
    if not message:
        return

    decoded_message = decode_message(message)
    logging.debug('Posting chat message: %s', decoded_message)

    # open shared memory
    try:
        shm = shared_memory.SharedMemory("rF2_ChatTransceiver_SM", create=False)
    except FileNotFoundError:
        return

    destination = 0  # message center

    # make sure message does not exceed message size
    mem_bytes = f'{destination}{decoded_message[:128]}'.encode('cp1252')

    # write to shared memory
    shm.buf[:len(mem_bytes)] = mem_bytes
    logging.debug('Writing to shared memory: %s', mem_bytes)

    shm.close()


@capture_app_exceptions
def install_plugin():
    plugin_path = get_data_dir() / CHAT_PLUGIN_NAME
    target_path = Path(_get_rf_location(RFACTOR_PLUGIN_PATH))
    logging.debug('Installing Chat Plugin to: %s', target_path)
    shutil.copy(plugin_path, target_path)


@capture_app_exceptions
def uninstall_plugin():
    plugin_path = Path(_get_rf_location(RFACTOR_PLUGIN_PATH)) / CHAT_PLUGIN_NAME
    logging.debug('Uninstalling Chat Plugin from: %s', plugin_path)
    if plugin_path.exists() and plugin_path.is_file():
        plugin_path.unlink()


@capture_app_exceptions
def get_plugin_version():
    plugin_path = Path(_get_rf_location(RFACTOR_PLUGIN_PATH)) / CHAT_PLUGIN_NAME

    if plugin_path.exists() and plugin_path.is_file():
        version = AppSettings.chat_plugin_version.get(get_file_hash(plugin_path))
        logging.debug('Found ChatTransceiver Plugin version: %s', version)
        return json.dumps({'result': True, 'version': version})

    return json.dumps({'result': False})
