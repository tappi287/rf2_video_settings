import csv
import logging
import statistics
import sys
import threading
import time
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Optional, Iterator, Tuple, Any, List

from rf2settings.app_settings import AppSettings
from rf2settings.globals import get_present_mon_bin
from rf2settings.preset.preset_base import PRESET_TYPES, load_presets_from_dir
from rf2settings.rf2command import Command, CommandQueue
from rf2settings.utils import percentile
from .directInputKeySend import rfKeycodeToDIK
from .preset.preset import GraphicsPreset, SessionPreset, PresetType
from .preset.presets_dir import get_user_presets_dir
from .preset.settings_model import BaseOptions, BenchmarkControllerJsonSettings, BenchmarkSettings
from .process import RunProcess
from .rf2connect import RfactorState
from .rf2events import StartBenchmarkEvent, RecordBenchmarkEvent, RfactorQuitEvent, RfactorStatusEvent
from .rfactor import RfactorPlayer

"""
base_url = 'localhost'
web_ui_port = 5397

Start race session: POST
/rest/race/startRace
r = RfactorConnect.post_request('/rest/race/startRace')

Drive: POST
/rest/garage/drive
r = RfactorConnect.post_request('/rest/garage/drive')

Get replay dict: GET
/rest/watch/replays

Load and play replay: GET
/rest/watch/play/<replay_id>'

Switch to fullscreen: POST (with data=None)
/navigation/action/NAV_TO_FULL_EVENT_MONITOR

Navigate to garage: POST
/navigation/action/NAV_TO_GARAGE

Next session: POST
/navigation/action/NAV_NEXT_SESSION

Switch to MAIN MENU: POST (with data=None)
/navigation/action/NAV_TO_MAIN_MENU

Quit the game: POST (with data=None)
/rest/start/quitGame

Get Tracks: GET
/rest/race/track?locale=en-US
Set Track: POST, data=track_id
/rest/race/track
Get Series GET
/rest/race/series
v1124
Set Series POST data=series_id
/rest/race/series
v1125
/rest/race/series?signature=series_id
Get Cars GET
/rest/race/car
Set Cars POST: data=car_id
/rest/race/car

SESSION SETTINGS
Get
/rest/sessions GET
Race Time
/rest/sessions/settings POST {'sessionSetting': 'SESSSET_race_starting_time', 'value': 1}
Grid Position
/rest/sessions/settings POST {'sessionSetting': 'SESSSET_Grid_Position', 'value': 1}

Get selection
/rest/race/selection?locale=en-US
Get Profile
/rest/profile
"""


def _create_benchmark_commands(ai_key, fps_key):
    # Wait for UI
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=120.0))

    # -- Set session settings
    CommandQueue.append(Command(Command.set_session_settings, data=AppSettings.session_selection, timeout=5.0))
    # -- Reset Session Settings
    AppSettings.session_selection = dict()

    # -- Set Content
    CommandQueue.append(Command(Command.set_content, data=AppSettings.content_selected, timeout=5.0))
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
    # Timeout
    CommandQueue.append(Command(Command.timeout_command, data=5, timeout=12.0))
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


class RfactorBenchmark:
    running = False
    recording = False
    rf_changed_from_live = False

    # -- Keyboard Mappings to be read from rF2
    ai_key = 'Control - Toggle AI Control'
    ai_dik = ''
    fps_key = 'Control - Framerate'
    fps_dik = ''

    present_mon_bin = get_present_mon_bin()
    present_mon_result_dir: Path = get_user_presets_dir() / 'benchmark_results'
    default_benchmark_length = 50

    def __init__(self, rf: Optional[RfactorPlayer] = None, setting_name: str = None, setting_value: str = None):
        """ Helper to run the rFactor 2 DEV executable with the current Session Settings,
            most likely rF Trainer @ Loch Drummond, for a fixed amount of time in a quick race with AI control.

            :param rf: RfactorPlayer instance to use
            :param setting_name: optional setting name to name the result file "rf2_settingName_settingValue"
            :param setting_value: optional setting value to name result file "rf2_settingName_settingValue"
        """
        self.kill_pm_event = threading.Event()
        self.kill_event = threading.Event()
        self.present_mon_process: Optional[threading.Thread] = None

        self.rf = rf or RfactorPlayer()

        # Prepare settings to be applied
        self.current_session_preset = SessionPreset()
        self.setting_name, self.setting_value = setting_name, setting_value

        self.result_file: Optional[Path] = None
        self.benchmark_length = self.default_benchmark_length
        self.start_time = 0.0

        self._timestamp = 0

    def event_loop(self):
        # -- Receive Start Benchmark Event from FrontEnd
        if StartBenchmarkEvent.event.is_set() and not self.running:
            StartBenchmarkEvent.reset()
            self.run()

        # -- Receive Recording Event
        if RecordBenchmarkEvent.event.is_set() and self.running:
            logging.info('Starting to record benchmark with PresentMon')
            RecordBenchmarkEvent.reset()
            if not self.start_present_mon_logging():
                self.finish()
        else:
            RecordBenchmarkEvent.reset()

        # -- End Benchmark after benchmark length
        if self.recording and self.start_time > 0.0:
            remaining = (self.benchmark_length + 1) - (time.time() - self.start_time)
            RfactorStatusEvent.set(f'Recording Benchmark: {remaining:.0f}s remaining.')

            if remaining <= 0.0:
                logging.info('Benchmark is requesting rF2 quit.')
                RfactorQuitEvent.set(True)
                self.start_time = 0.0

        # -- If we were live before, close Benchmark
        if self.rf_changed_from_live and self.recording:
            RfactorStatusEvent.set(f'Benchmark finished.')
            self.rf_changed_from_live = False
            self.finish()

    def run(self):
        """ Run the benchmark """
        if not self._prepare_benchmark_run():
            logging.info('Preparing Benchmark run unsuccessful. Aborting...')
            self.finish()
            return

        logging.debug('Prepared Benchmark run. Starting rFactor 2')
        # -- Start rFactor 2
        result = self.rf.run_rfactor(method=1)
        if not result:
            logging.error('Rfactor 2 could not be started aborting benchmark run.')
            self.finish()
            return

        _create_benchmark_commands(self.ai_dik, self.fps_dik)
        self.running = True

    def start_present_mon_logging(self) -> bool:
        new_name = f'{datetime.now().strftime("%Y%m%d-%H-%M")}_rF2_benchmark.csv'
        self.result_file = self.present_mon_result_dir / new_name
        if not self.present_mon_result_dir.exists():
            self.present_mon_result_dir.mkdir(exist_ok=True)

        cmd = [self.present_mon_bin.as_posix(),
               '-process_name', 'rFactor2.exe', '-output_file', str(WindowsPath(self.result_file)),
               '-timed', str(int(self.benchmark_length)), '-no_top', '-qpc_time',
               '-terminate_after_timed', '-stop_existing_session']  # '-no_track_display'
        cwd = self.rf.location

        if self.present_mon_process is None:
            logging.info('Starting PresentMon: %s', cmd)
            self.kill_pm_event.clear()
            self.present_mon_process = RunProcess(cmd, cwd, self.kill_pm_event)
            self.present_mon_process.start()
            self.start_time = time.time()
            self.recording = True
            return True
        return False

    def finish(self):
        logging.info('rF Benchmark stopped and will collect results.')

        # -- Kill Running related processes
        self.abort()
        
        # -- Write Session and Graphics Settings to file
        if self.recording and self.result_file is not None:
            self._create_result()

        logging.info('rF2 Benchmark Run finished.')
        self.running = False
        self.recording = False

    def abort(self):
        self.kill_event.set()
        self.kill_pm_event.set()
        if self.present_mon_process is not None:
            self.present_mon_process.join(timeout=10)
            self.present_mon_process = None

        logging.info('rF2 Benchmark aborted. Kill event send.')

    def _prepare_benchmark_run(self) -> bool:
        """ Prepare rF settings and read keyboard assignments """
        result = True

        self.recording = False
        self.running = False

        # -- Read Benchmark App Settings
        benchmark_settings = BenchmarkSettings()
        benchmark_settings.from_js_dict(AppSettings.benchmark_settings)
        length = getattr(benchmark_settings.get_option('Length'), 'value', None)
        self.benchmark_length = int(length or self.default_benchmark_length)

        # -- Get Keyboard Assignments for AI Control and FPS View
        return self._update_controller_assignment() and result

    def _update_controller_assignment(self) -> bool:
        """ Read the current assignments for AI Control and Show FPS Counter """
        if not self.rf.is_valid:
            return False

        key = BenchmarkControllerJsonSettings.app_key
        if hasattr(self.rf.options, key):
            options = getattr(self.rf.options, key)
            for con_key in (self.ai_key, self.fps_key):
                o = options.get_option(con_key)
                if o and isinstance(o.value, list) and len(o.value) > 1:
                    if con_key == self.ai_key:
                        self.ai_dik = rfKeycodeToDIK(o.value[1])
                    elif con_key == self.fps_key:
                        self.fps_dik = rfKeycodeToDIK(o.value[1])
                    result = True
                    logging.debug('Read controller assignment %s: %s', con_key, rfKeycodeToDIK(o.value[1]))
                else:
                    result = False
            return result
        return False
    
    def _create_result(self):
        for preset_type in (PresetType.session, PresetType.graphics):
            current_preset = PRESET_TYPES.get(preset_type)()
            selected_preset_name = AppSettings.selected_presets.get(str(preset_type)) or current_preset.name
            _, selected_preset = load_presets_from_dir(get_user_presets_dir(), preset_type,
                                                       selected_preset_name=selected_preset_name)
            
            # -- Write preset next to result
            if selected_preset:
                file_name = f'{self.result_file.stem}_{selected_preset.prefix}_preset'
                if selected_preset.export(file_name, self.result_file.parent):
                    logging.debug('Exporting benchmark result preset: %s', file_name)
                else:
                    logging.error('Could not export benchmark result preset.')
            else:
                logging.error('Could not export benchmark result preset.')

    @staticmethod
    def iterate_preset_options(preset: GraphicsPreset) -> Iterator[Tuple[str, BaseOptions]]:
        for key in preset.option_class_keys:
            yield key, getattr(preset, key)

    @classmethod
    def edit_preset_option(cls, preset, setting_key: str, value: Any):
        for (option_cls_key, option_cls) in cls.iterate_preset_options(preset):
            o = [o for o in option_cls.options if o.key == setting_key]
            if len(o):
                o = o[0]
                o.value = value

    @staticmethod
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


# Set of settings to benchmark
# List[Tuple[str, str, Any, Optional[str]]]
# Do not use _ in names! Result printer will split result.csv file names at _
pp_set = [('EPostProcessingSettings', 'Post-Effects', 1, '0'),
          ('EPostProcessingSettings', 'Post-Effects', 2, '1'),
          ('EPostProcessingSettings', 'Post-Effects', 3, '2'),
          ('EPostProcessingSettings', 'Post-Effects', 4, '3'),
          ('EPostProcessingSettings', 'Post-Effects', 5, '4')]
shadow_set = [('Shadows', 'Shadows', 0, None),
              ('Shadows', 'Shadows', 1, None),
              ('Shadows', 'Shadows', 2, None),
              ('Shadows', 'Shadows', 3, None),
              ('Shadows', 'Shadows', 4, None), ]
shadow_blur_set = [('Shadow Blur', 'Shadow-Blur', 2, None), ('Shadow Blur', 'Shadow-Blur', 3, None), ]
msaa_set = [('FSAA', 'MSAA', 0, '0'), ('FSAA', 'MSAA', 32, '1'),
            ('FSAA', 'MSAA', 33, '2'), ('FSAA', 'MSAA', 34, '3'),
            ('FSAA', 'MSAA', 35, '4'), ('FSAA', 'MSAA', 36, '5')]


def _test_benchmark(settings: List[Tuple[str, str, Any, Optional[str]]]):
    from rf2settings.preset.preset_base import load_preset
    bench_preset = load_preset(Path('./default_presets/gfx_VR-Low.json'), GraphicsPreset.preset_type)

    RfactorBenchmark.edit_preset_option(bench_preset, 'EPostProcessingSettings', 2)
    RfactorBenchmark.edit_preset_option(bench_preset, 'Shadows', 3)

    for setting in settings:
        key, name, value, value_name = setting

        # Adjust rF2 settings
        RfactorBenchmark.edit_preset_option(bench_preset, key, value)

        # Run the benchmark
        rb = RfactorBenchmark(preset=bench_preset, setting_name=name, setting_value=value_name or str(value))
        rb.run()


if __name__ == '__main__':
    """
        THIS WILL DISABLE ctypes support! But it will make sure "Launch rFactor2" 
        or basically any executable that is loading DLLs will work.
    """
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.SetDllDirectoryA(None)
    """
        //
    """
    test_settings = pp_set[0:3] + shadow_set[0:3] + msaa_set[2:]
    _test_benchmark(test_settings)
