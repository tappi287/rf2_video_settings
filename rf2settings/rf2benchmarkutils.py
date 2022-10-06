import csv
import logging
import statistics
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

from rf2settings.app_settings import AppSettings
from rf2settings.globals import get_fpsvr_dir, FPSVR_APPID
from rf2settings.preset.preset import BasePreset, GraphicsPreset, SessionPreset
from rf2settings.preset.preset_base import load_preset
from rf2settings.preset.settings_model import BenchmarkSettings
from rf2settings.rf2command import Command, CommandQueue
from rf2settings.rf2connect import RfactorState
from rf2settings.utils import percentile
from rf2settings.valve.steam_utils import SteamApps


class BenchmarkRun:
    id_counter = 0

    def __init__(self, name: str = None, presets: List[BasePreset] = None, settings: BenchmarkSettings = None):
        BenchmarkRun.id_counter += 1
        self.id = BenchmarkRun.id_counter
        self.name = name or str()
        self.presets: List[BasePreset] = presets or list()
        self.settings: BenchmarkSettings = settings or BenchmarkSettings()


class BenchmarkQueue:
    queue: List[BenchmarkRun] = list()

    @classmethod
    def is_empty(cls):
        return len(cls.queue) == 0

    @classmethod
    def append(cls, run: BenchmarkRun):
        cls.queue.append(run)

    @classmethod
    def remove(cls, entry_id: int):
        for run in cls.queue:
            if run.id == entry_id:
                cls.queue.remove(run)
                return True
        return False

    @classmethod
    def next(cls) -> Optional[BenchmarkRun]:
        if not cls.is_empty():
            run = cls.queue.pop(0)
            run.name = f'{datetime.now().strftime("%Y%m%d-%H-%M")}_rF2_benchmark'
            return run

    @classmethod
    def reset(cls):
        cls.queue = list()


def create_benchmark_commands(ai_key: str, fps_key: str, recording_timeout: int, replay: Optional[str] = None):
    # Wait for UI
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=120.0))

    if replay is None:
        # -- Set session settings
        CommandQueue.append(Command(Command.set_session_settings, data=AppSettings.session_selection, timeout=10.0))
        # -- Set Content
        CommandQueue.append(Command(Command.set_content, data=AppSettings.content_selected, timeout=10.0))
        # Start Race Session
        CommandQueue.append(Command(Command.start_race, timeout=10.0))

    # -- Reset Session Settings
    AppSettings.session_selection = dict()
    # -- Reset Content Selection
    AppSettings.content_selected = dict()

    if replay is not None:
        # -- Load Replay
        CommandQueue.append(Command(Command.play_replay, data=replay, timeout=30.0))

    # Wait UI Loading State
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.loading, timeout=90.0))
    # Wait UI Ready State
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=800.0))

    if replay is not None:
        # 5. Switch FullScreen
        CommandQueue.append(Command(Command.switch_fullscreen, timeout=30.0))
    else:
        # Drive
        CommandQueue.append(Command(Command.drive, timeout=10.0))
        # Timeout
        CommandQueue.append(Command(Command.timeout_command, data=2, timeout=10.0))
        # Ai Control
        CommandQueue.append(Command(Command.press_key, data=ai_key, timeout=12.0))

    # Recording Timeout
    CommandQueue.append(Command(Command.timeout_command, data=recording_timeout, timeout=12.0))
    # Present mon record
    CommandQueue.append(Command(Command.record_benchmark, timeout=20.0))
    """
    # FPS Measure
    CommandQueue.append(Command(Command.press_ctrl_key, data=fps_key, timeout=12.0))
    # Timeout
    CommandQueue.append(Command(Command.timeout_command, data=20, timeout=10.0))
    # Record Performance
    CommandQueue.append(Command(Command.press_shift_key, data='DIK_SPACE', timeout=10.0))
    """


def read_present_mon_result(file: Path, details: bool = False):
    required_fields = {'msUntilDisplayed', 'QPCTime', 'msUntilRenderComplete', 'msBetweenDisplayChange',
                       'Dropped', 'msInPresentAPI', 'TimeInSeconds', 'msBetweenPresents'}
    non_detail_fields = {'msBetweenPresents', }

    data = dict()
    with open(file, newline='') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if row[0].startswith('//'):
                # -- Skip comment rows
                continue
            if not data:
                # -- Assume first line as Header with column names
                for field_name in row:
                    data[field_name] = list()
                continue

            # -- Collect data for every row
            for field_value, field_name in zip(row, data.keys()):
                if not details and field_name not in non_detail_fields:
                    continue
                if field_value.replace('.', '', 1).isdigit():
                    field_value = float(field_value)
                if field_name in required_fields:
                    data[field_name].append(field_value)

    # -- Remove unnecessary fields
    for key in set(data.keys()):
        if key not in required_fields:
            data.pop(key)

    # -- FPS
    data['fps'] = [1000 / i for i in data['msBetweenPresents']]

    # -- Statistics
    sorted_fps = sorted(data['fps'])
    data['fps99'] = percentile(sorted_fps, 99)
    data['fps98'] = percentile(sorted_fps, 98)
    data['fps002'] = percentile(sorted_fps, 0.2)
    data['fpsmean'], data['fpsmedian'] = statistics.mean(sorted_fps), statistics.median(sorted_fps)

    if not details:
        data.pop('msBetweenPresents')
        data.pop('fps')

    return data


def read_preset_result(result_file: Path) -> Dict[int, BasePreset]:
    presets = dict()
    gfx = (GraphicsPreset.preset_type, GraphicsPreset.prefix)
    ses = (SessionPreset.preset_type, SessionPreset.prefix)

    for preset_type, prefix in (gfx, ses):
        for f in result_file.parent.glob(f'{result_file.stem}*{prefix}.json'):
            logging.debug('Located result preset: %s', f.name)
            p = load_preset(f, preset_type)
            presets[preset_type] = None if not p else p.to_js()

    return presets


class FpsVR:
    initial_loading_timeout = 30.0
    loading_timeout = 25.0
    benchmark_length = 60.0
    FPS_VR_CMD_EXE = 'fpsVRcmd.exe'

    def __init__(self, target_result_name: str = None):
        """ Start/stop frame data logging and collect file name of the resulting
            CSV fpsVR file.
        """
        self.fps_vr_cmd = Path()
        self._get_fpsvr_cmd()

        # Keep an index of csv files present before the current benchmark
        # so we can identify the new created one.
        self.fpsvr_csv_index = set()

        self.result_csv_file = Path()
        self.target_result_name = target_result_name

    def start(self):
        """ Run the benchmark for _benchmark_length_ seconds. """
        # -- Start fpsVR logging
        self._index_fpsvr_csv_dir()
        self.start_stop_fpsvr_logging()

        # -- Wait for _benchmark_length_ seconds
        logging.info('rF Benchmark started logging.')

    def stop(self):
        # -- Stop Benchmark
        self.start_stop_fpsvr_logging()
        self.close()
        logging.info('FPS VR stopped logging and will collect results.')
        time.sleep(1)  # Give fpsVR some time to write the results
        self._collect_result()

    def start_stop_fpsvr_logging(self):
        if not self.fps_vr_cmd.exists():
            return

        args = [self.fps_vr_cmd, 'logging_startstop']
        try:
            subprocess.Popen(args)
        except Exception as e:
            logging.error('Error starting fpsVR frames logging: %s', e)

    def _collect_result(self):
        if not self.fps_vr_cmd.exists():
            return

        for file in get_fpsvr_dir().glob('*.csv'):
            if file.name not in self.fpsvr_csv_index:
                self.result_csv_file = file
                break

        # -- Rename result file
        if self.result_csv_file.exists() and self.target_result_name:
            target_path = self.result_csv_file.with_stem(
                f'{self.target_result_name}_{datetime.strftime(datetime.now(), "%Y-%m-%dT%H%M%S")}'
            )
            self.result_csv_file.rename(target_path)

    def _index_fpsvr_csv_dir(self):
        if not self.fps_vr_cmd.exists():
            return

        for file in get_fpsvr_dir().glob('*.csv'):
            self.fpsvr_csv_index.add(file.name)

    def _get_fpsvr_cmd(self):
        s = SteamApps()
        path = s.find_game_location(FPSVR_APPID)

        if path and path.exists():
            self.fps_vr_cmd = path / self.FPS_VR_CMD_EXE
