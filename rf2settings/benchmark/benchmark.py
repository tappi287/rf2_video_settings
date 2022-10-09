import json
import logging
import shutil
import threading
import time
from pathlib import Path, WindowsPath
from typing import Optional

import gevent

from rf2settings.app_settings import AppSettings
from rf2settings.directInputKeySend import rfKeycodeToDIK
from rf2settings.preset.preset import PresetType, GraphicsPreset
from rf2settings.preset.preset_base import PRESET_TYPES, load_presets_from_dir
from rf2settings.preset.presets_dir import get_user_presets_dir
from rf2settings.preset.settings_model import BenchmarkControllerJsonSettings
from rf2settings.process import RunProcess
from rf2settings.benchmark.benchmark_utils import create_benchmark_commands, BenchmarkRun, BenchmarkQueue
from rf2settings.benchmark.fpsvr import FpsVR
from rf2settings.rf2connect import RfactorConnect, RfactorState
from rf2settings.rf2events import StartBenchmarkEvent, RecordBenchmarkEvent, RfactorQuitEvent
from rf2settings.rf2events import RfactorStatusEvent, BenchmarkProgressEvent
from rf2settings.rfactor import RfactorPlayer
from rf2settings.utils import create_file_safe_name


# TODO: Abort button


class RfactorBenchmark:
    running = False
    recording = False

    # -- Keyboard Mappings to be read from rF2
    ai_key = 'Control - Toggle AI Control'
    ai_dik = ''
    fps_key = 'Control - Framerate'
    fps_dik = ''

    default_benchmark_length = 50
    default_timeout = 12

    def __init__(self, rf: Optional[RfactorPlayer] = None):
        """ Helper to run the rFactor 2 DEV executable with the current Session Settings,
            most likely rF Trainer @ Loch Drummond, for a fixed amount of time in a quick race with AI control.

            :param rf: RfactorPlayer instance to use
        """
        self.kill_pm_event = threading.Event()
        self.kill_event = threading.Event()
        self.present_mon_process: Optional[RunProcess] = None

        self.rf = rf or RfactorPlayer()

        self.current_run: BenchmarkRun = BenchmarkRun()

        self.fps_vr: Optional[FpsVR] = None

        self.result_file: Optional[Path] = None
        self.benchmark_length = self.default_benchmark_length
        self.recording_timeout = self.default_timeout
        self.replay: Optional[str] = None
        self.use_fps_vr = False
        self.start_time = 0.0

        self._timestamp = 0

    def event_loop(self):
        # -- Receive Start Benchmark Event from FrontEnd or Queue
        if StartBenchmarkEvent.event.is_set() and not self.running and RfactorConnect.state == RfactorState.unavailable:
            StartBenchmarkEvent.reset()
            BenchmarkProgressEvent.set({'progress': 10, 'size': len(BenchmarkQueue.queue)})
            self.run()

        # -- Receive Recording Event
        if RecordBenchmarkEvent.event.is_set() and self.running:
            RecordBenchmarkEvent.reset()
            if self.use_fps_vr:
                logging.info('Starting to record benchmark with FpsVR')
                if not self.start_fpsvr_logging():
                    self.finish()
            else:
                logging.info('Starting to record benchmark with PresentMon')
                if not self.start_present_mon_logging():
                    self.finish()

        # -- End Benchmark after benchmark length
        if self.recording and self.start_time > 0.0:
            remaining = self.benchmark_length - (time.time() - self.start_time)
            RfactorStatusEvent.set(f'Recording Benchmark: {remaining:.0f}s remaining.')

            percent = round(max(0.0, self.benchmark_length + 10.0 - remaining) * 100 /
                            max(1.0, self.benchmark_length + 10.0))
            BenchmarkProgressEvent.set({'progress': min(100, percent), 'size': len(BenchmarkQueue.queue)})

            if remaining <= 0.0:
                logging.info('Detected end of Benchmark Recording Time.')
                self.start_time = 0.0
                self.finish()

        # -- End Benchmark if PresentMon process finished
        if self.present_mon_process is not None and self.present_mon_process.event.is_set():
            logging.info('Detected end of Benchmark Recording process.')
            self.finish()

    def get_current_gfx_preset(self) -> GraphicsPreset:
        for preset in self.current_run.presets:
            if preset.preset_type == PresetType.graphics:
                return preset

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

        create_benchmark_commands(self.ai_dik, self.fps_dik, self.recording_timeout, self.replay)
        self.running = True

    def finish(self):
        logging.info('rF Benchmark stopped and will collect results.')
        if self.use_fps_vr:
            self.fps_vr.stop()
            self._collect_fps_vr_result()

        # -- Kill Running related processes
        self.abort()

        # -- Write Session and Graphics Settings to file
        if self.recording and self.result_file is not None:
            self._create_result()

        logging.info('rF2 Benchmark Run finished.')
        self.running = False
        self.recording = False

        if not BenchmarkQueue.is_empty():
            logging.info('Found items in Benchmark Queue. Triggering StartBenchmark event.')
            StartBenchmarkEvent.set(True)
            gevent.sleep(2)
        else:
            BenchmarkProgressEvent.set({'progress': 0, 'size': 0})

    def abort(self):
        logging.info('Benchmark is requesting rF2 quit.')
        RfactorQuitEvent.set(True)

        self.kill_event.set()
        self.kill_pm_event.set()
        if self.present_mon_process is not None:
            self.present_mon_process.join(timeout=10)
            self.present_mon_process = None

        logging.info('rF2 Benchmark aborted. Kill event send.')

    def _prepare_benchmark_run(self) -> bool:
        """ Prepare rF settings, apply presets and read keyboard assignments """
        result = True

        self.recording = False
        self.running = False

        # -- Get next run from the queue
        self.current_run = BenchmarkQueue.next()
        if not self.current_run:
            logging.info('No more Benchmark runs in the queue!')
            return False

        # -- Apply current presets
        preset_names = list()
        for preset in self.current_run.presets:
            if self.rf.is_valid:
                logging.info('Applying benchmark preset: %s', preset.name)
                if not self.rf.write_settings(preset):
                    logging.error('Could not write current Preset settings to rFactor %s', self.rf.error)
                    return False
                # -- Update WebUi Session Settings from current preset
                AppSettings.update_webui_settings(self.rf)
                preset_names.append(preset.name)

        # -- Apply Benchmark Settings
        length = getattr(self.current_run.settings.get_option('Length'), 'value', None)
        timeout = getattr(self.current_run.settings.get_option('TimeOut'), 'value', None)
        self.replay = getattr(self.current_run.settings.get_option('Replay'), 'value', None)
        self.use_fps_vr = getattr(self.current_run.settings.get_option('use_fps_vr'), 'value', False)
        self.benchmark_length = int(length or self.default_benchmark_length)
        self.recording_timeout = int(timeout or self.default_timeout)

        logging.info('Prepared Benchmark Run: %s length %s recording delay %s replay %s with Presets: %s',
                     self.current_run.name, self.benchmark_length, self.recording_timeout, self.replay,
                     preset_names)

        if not AppSettings.present_mon_result_dir.exists():
            AppSettings.present_mon_result_dir.mkdir()

        if self.use_fps_vr:
            self.fps_vr = FpsVR(create_file_safe_name(self.get_current_gfx_preset().name))
            logging.info('Using FpsVR for measurements.')

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

    def _collect_fps_vr_result(self):
        file = self.fps_vr.get_result_file()
        if not file:
            return
        target = AppSettings.present_mon_result_dir / file.name
        shutil.move(file, target)
        self.result_file = target

    def _create_result(self):
        if not self.result_file.exists():
            logging.info('Could not locate PresentMon result file. Skipping creation of result Preset files.')
            return

        preset_names = []
        for preset_type in (PresetType.session, PresetType.graphics):
            current_preset = PRESET_TYPES.get(preset_type)()
            selected_preset_name = AppSettings.selected_presets.get(str(preset_type)) or current_preset.name
            _, selected_preset = load_presets_from_dir(get_user_presets_dir(), preset_type,
                                                       selected_preset_name=selected_preset_name)
            if not selected_preset and preset_type == PresetType.graphics:
                selected_preset = self.get_current_gfx_preset()
            preset_names.append(selected_preset_name)

            # -- Write preset next to result
            if selected_preset:
                file_name = f'{self.result_file.stem}_{selected_preset.prefix}'
                if selected_preset.export(file_name, self.result_file.parent, keep_export_data=True):
                    logging.debug('Exporting benchmark result preset: %s', file_name)
                else:
                    logging.error('Could not export benchmark result preset.')
            else:
                logging.error('Could not export benchmark result preset.')

        # -- Export Benchmark Settings
        options = list()
        options.append({'name': 'rF2 Version', 'value': AppSettings.last_rf_version})
        options.append({'name': 'Benchmark Length', 'value': f'{self.benchmark_length}s'})
        options.append({'name': 'Recording Delay', 'value': f'{self.recording_timeout}s'})
        options.append({'name': 'Replay', 'value': f'{self.replay or "None"}'})
        options.append({'name': 'Original Session Preset Name', 'value': preset_names[0]})
        options.append({'name': 'Original Gfx Preset Name', 'value': preset_names[1]})

        file = self.result_file.parent / f'{self.result_file.stem}_settings.json'
        try:
            with open(file, 'w') as f:
                json.dump(options, f, indent=2, sort_keys=True)
                logging.debug('Exporting benchmark result settings: %s', file.name)
        except Exception as e:
            logging.error('Could not write benchmark result settings: %s', e)

    def start_fpsvr_logging(self):
        if self.fps_vr.start():
            self.start_time = time.time()
            self.recording = True
            return True
        return False

    def start_present_mon_logging(self) -> bool:
        self.result_file = AppSettings.present_mon_result_dir / f'{self.current_run.name}.csv'
        cmd = [AppSettings.present_mon_bin.as_posix(),
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

        logging.info('Instance of PresentMon process is already present. Can not start Benchmark Recording.')
        return False
