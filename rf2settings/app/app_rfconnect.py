import json
import logging
import re
from datetime import datetime
from pathlib import Path

import eel
import gevent

from ..app_settings import AppSettings
from ..preset.preset import PresetType
from ..preset.preset_base import load_presets_from_dir
from ..preset.presets_dir import get_user_presets_dir
from ..rf2command import CommandQueue, Command
from ..rf2connect import RfactorState
from ..rf2events import RfactorQuitEvent, StartBenchmarkEvent
from ..rfactor import RfactorPlayer
from ..utils import create_file_safe_name


def expose_rfconnect_methods():
    """ empty method we import to have the exposed methods registered """
    pass


def apply_gfx_preset_with_name(rf: RfactorPlayer, preset_name: str) -> bool:
    _, selected_preset = load_presets_from_dir(get_user_presets_dir(), PresetType.graphics,
                                               selected_preset_name=preset_name)
    if selected_preset:
        rf.write_settings(selected_preset)
        eel.sleep(0.01)
        return True
    return False


@eel.expose
def quit_rfactor():
    result = False
    RfactorQuitEvent.set(True)
    try:
        result = RfactorQuitEvent.quit_result.get(timeout=20.0)
    except gevent.Timeout:
        pass

    if result:
        return json.dumps({'result': True})
    else:
        return json.dumps({'result': False})


@eel.expose
def get_replays():
    rf = RfactorPlayer()
    if not rf.is_valid:
        return json.dumps({'result': False, 'msg': rf.error})

    p = rf.location / 'UserData' / 'Replays'
    replays = list()

    for idx, r in enumerate(p.glob('*.Vcr')):
        s = r.stat()

        # Determine type by name
        replay_type = 0
        if re.match(r".*(HOT\sLAP)", r.stem):
            replay_type = 4  # Hot Lap
        elif re.match(r".*(Q\d)\s.*", r.stem):
            replay_type = 1  # Qualy
        elif re.match(r".*(P\d)\s.*", r.stem):
            replay_type = 2  # Practice
        elif re.match(r".*(R\d)\s.*", r.stem):
            replay_type = 3  # Race
        elif re.match(r".*(WU\s\d)", r.stem):
            replay_type = 5  # WarmUp

        replay = {'id': idx, 'name': r.stem, 'size': f'{s.st_size / 1048576:.2f}MB',
                  'ctime': s.st_mtime, 'type': replay_type,
                  'date': datetime.fromtimestamp(s.st_mtime).strftime('%Y-%m-%d %H:%M')}
        replays.append(replay)

    # Sort by change date
    replays = sorted(replays, key=lambda e: e['ctime'], reverse=True)

    return json.dumps({'result': True, 'replays': replays})


@eel.expose
def get_replay_preset():
    logging.debug('Providing replay preset name: %s', AppSettings.replay_preset)
    return AppSettings.replay_preset


@eel.expose
def set_replay_preset(preset_name):
    AppSettings.replay_preset = preset_name
    logging.debug('Updated replay preset name to: %s', AppSettings.replay_preset)
    AppSettings.save()


@eel.expose
def play_replay(replay_name):
    if not replay_name:
        return json.dumps({'result': False, 'msg': 'No Replay name provided.'})

    rf = RfactorPlayer()
    if not rf.is_valid:
        return json.dumps({'result': False, 'msg': rf.error})

    # -- Check rF2 version > 1122
    version = rf.version.replace('\n', '')
    if not version >= '1.1122':
        logging.debug('rf Version: ', rf.version)
        return json.dumps({'result': False, 'msg': f'Watching replays with this App is not support with rFactor 2 '
                                                   f'versions without the newUI. Your version: {version}'})

    # -- Apply replay graphics preset
    apply_gfx_preset_with_name(rf, AppSettings.replay_preset)

    # -- Start rFactor 2
    result = rf.run_rfactor()
    if not result:
        # -- Restore non-replay graphics preset
        selected_preset_name = AppSettings.selected_presets.get(str(PresetType.graphics))
        apply_gfx_preset_with_name(rf, selected_preset_name)
        logging.info('Restored non-replay preset %s', selected_preset_name)
        return json.dumps({'result': False, 'msg': f'Could not launch rF2: {rf.error}'})

    # -- Tell the rFactor Greenlet to play a replay in next iteration
    # 1. Wait for UI
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=30.0))
    # 2. Load Replay
    CommandQueue.append(Command(Command.play_replay, replay_name, timeout=30.0))
    # 3. Wait UI Loading State
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.loading, timeout=30.0))
    # 4. Wait UI Ready State
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=800.0))
    # 5. Switch FullScreen
    CommandQueue.append(Command(Command.switch_fullscreen, timeout=30.0))

    return json.dumps({'result': True, 'msg': rf.error})


@eel.expose
def delete_replays(replays: list):
    rf = RfactorPlayer()
    if not rf.is_valid:
        return json.dumps({'result': False, 'msg': rf.error})

    errors = list()
    p: Path = rf.location / 'UserData' / 'Replays'
    for r in replays:
        try:
            replay_file: Path = p / f"{r.get('name', '')}.Vcr"
            if replay_file.exists():
                logging.debug('Deleting replay: %s', replay_file.as_posix())
                replay_file.unlink()
        except Exception as e:
            logging.error('Error deleting replay: %s', e)
            errors.append(f'Error deleting replay: {e}')

    if errors:
        return json.dumps({'result': False, 'msg': '; '.join(errors)})

    return json.dumps({'result': True})


@eel.expose
def rename_replay(replay: dict, new_name: str):
    if not new_name:
        return json.dumps({'result': False, 'msg': 'Enter a name containing at least one character.'})

    rf = RfactorPlayer()
    if not rf.is_valid:
        return json.dumps({'result': False, 'msg': rf.error})

    try:
        p: Path = rf.location / 'UserData' / 'Replays'
        replay_file: Path = p / f"{replay.get('name', '')}.Vcr"
        target_file = replay_file.with_stem(create_file_safe_name(new_name, allow_spaces=True))
        replay_file.rename(target_file)
        logging.info('Renaming replay: %s to %s', replay.get('name'), target_file.as_posix())
    except Exception as e:
        logging.error('Error renaming replay: %s', e)
        return json.dumps({'result': False, 'msg': f'Error renaming replay: {e}'})

    return json.dumps({'result': True})
