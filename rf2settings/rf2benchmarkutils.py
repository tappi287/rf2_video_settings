import csv
import statistics
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from rf2settings.app_settings import AppSettings
from rf2settings.preset.preset import BasePreset
from rf2settings.preset.settings_model import BenchmarkSettings
from rf2settings.rf2command import Command, CommandQueue
from rf2settings.rf2connect import RfactorState
from rf2settings.utils import percentile


class BenchmarkRun:
    def __init__(self, name: str = None, presets: List[BasePreset] = None, settings: BenchmarkSettings = None):
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
    def next(cls) -> Optional[BenchmarkRun]:
        if not cls.is_empty():
            run = cls.queue.pop(0)
            run.name = f'{datetime.now().strftime("%Y%m%d-%H-%M")}_rF2_benchmark'
            return run

    @classmethod
    def reset(cls):
        cls.queue = list()


def create_benchmark_commands(ai_key: str, fps_key: str, recording_timeout: int):
    # Wait for UI
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=120.0))

    # -- Set session settings
    CommandQueue.append(Command(Command.set_session_settings, data=AppSettings.session_selection, timeout=10.0))
    # -- Reset Session Settings
    AppSettings.session_selection = dict()

    # -- Set Content
    CommandQueue.append(Command(Command.set_content, data=AppSettings.content_selected, timeout=10.0))
    # -- Reset Content Selection
    AppSettings.content_selected = dict()

    # Start Race Session
    CommandQueue.append(Command(Command.start_race, timeout=10.0))
    # Wait UI Loading State
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.loading, timeout=90.0))
    # Wait UI Ready State
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=800.0))
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


def read_present_mon_result(file: Path):
    required_fields = {'msUntilDisplayed', 'QPCTime', 'msUntilRenderComplete', 'msBetweenDisplayChange',
                       'Dropped', 'msInPresentAPI', 'TimeInSeconds', 'msBetweenPresents'}

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
    p99 = percentile(sorted(data['fps']), 99)
    p98 = percentile(sorted(data['fps']), 98)
    avg_fps, median_fps = statistics.mean(data['fps']), statistics.median(data['fps'])

    data['fps99'], data['fps98'] = p99, p98
    data['fpsmedian'] = median_fps
    data['fpsmean'] = avg_fps
    return data