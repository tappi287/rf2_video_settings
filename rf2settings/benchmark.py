import logging
import shutil
import threading
from pathlib import Path
from queue import Queue, Empty
from subprocess import Popen
from time import time, sleep
from typing import Optional

from .globals import get_fpsvr_dir, FPSVR_APPID
from .preset.preset import GraphicsPreset
from .process import RunProcess
from .rfactor import RfactorPlayer
from .valve.steam_utils import SteamApps


class RunRfactorBenchmark:
    initial_loading_timeout = 30.0
    loading_timeout = 25.0
    benchmark_length = 60.0

    result_dir = 'benchdata'

    def __init__(self, rf: Optional[RfactorPlayer] = None, preset: Optional[GraphicsPreset] = None,
                 setting_name: str = None, setting_value: str = None):
        """ Helper to run the rFactor 2 DEV executable with the current Session Settings,
            most likely rF Trainer @ Loch Drummond, for a fixed amount of time in a quick race with AI control.

            If fpsVR is present, will start/stop frame data logging and collect file name of the resulting
            CSV fpsVR file.

            :param rf: RfactorPlayer instance to use
            :param preset: the GraphicsPreset settings to apply
            :param setting_name: optional setting name to name the result file "rf2_settingName_settingValue"
            :param setting_value: optional setting value to name result file "rf2_settingName_settingValue"
        """
        self.kill_event = threading.Event()
        self.rf = rf or RfactorPlayer(dev=True)

        # Prepare settings to be applied
        self.benchmark_preset = preset
        self.current_preset = GraphicsPreset()
        self.current_preset.update(self.rf)
        self.setting_name, self.setting_value = setting_name, setting_value

        self.fps_vr_cmd = Path()
        self._get_fpsvr_cmd()

        # Keep an index of csv files present before the current benchmark
        # so we can identify the new created one.
        self.fpsvr_csv_index = set()

        self.result_csv_file = Path()

    def run(self):
        """ Run the benchmark for _benchmark_length_ seconds. """
        # -- Apply the benchmark settings
        if self.benchmark_preset is not None:
            self.rf.write_settings(self.benchmark_preset)

        # -- Start the rF DEV executable
        cwd = self.rf.location
        args = [self.rf.location / 'Bin64' / 'rFactor2 Mod Mode.exe',
                '+autotest', '-assert', '+skipmonitor', '+quickrace', '+grandprix']
        stdout_q = Queue()
        t = RunProcess(args, cwd, self.kill_event, stdout_q)
        t.start()

        # -- Wait for _loading_timeout_ seconds for the GrandPrix to be loaded
        logging.info('rF Benchmark is waiting for rF to load.')
        self.kill_event.wait(self.initial_loading_timeout)  # Wait an initial amount for executable to init
        timeout_start = time()
        while time() - timeout_start < self.loading_timeout:
            try:
                stdout_q.get(timeout=self.loading_timeout * 0.1)
            except Empty:
                pass
            else:
                # If we find output we assume rF to be still loading until timeout
                timeout_start = time()

        # -- Start fpsVR logging
        self._index_fpsvr_csv_dir()
        self.start_stop_fpsvr_logging()

        # -- Wait for _benchmark_length_ seconds
        logging.info('rF Benchmark started logging.')
        while time() - timeout_start < self.benchmark_length:
            self.kill_event.wait(self.benchmark_length*0.25)

        # -- Stop Benchmark
        self.start_stop_fpsvr_logging()
        self.close()
        logging.info('rF Benchmark stopped logging and will collect results.')
        sleep(1)  # Give fpsVR some time to write the results

        # -- Restore previous settings
        if self.benchmark_preset is not None:
            self.rf.write_settings(self.current_preset)

        self._collect_result()
        self._write_result()
        logging.info('rF Benchmark finished.')

    def close(self):
        self.kill_event.set()

    def start_stop_fpsvr_logging(self):
        if not self.fps_vr_cmd.exists():
            return

        args = [self.fps_vr_cmd, 'logging_startstop']
        try:
            Popen(args)
        except Exception as e:
            logging.error('Error starting fpsVR frames logging: %s', e)

    def _collect_result(self):
        if not self.fps_vr_cmd.exists():
            return

        for file in get_fpsvr_dir().glob('*.csv'):
            if file.name not in self.fpsvr_csv_index:
                self.result_csv_file = file
                break

    def _write_result(self) -> bool:
        if not self.result_csv_file.exists():
            return False

        try:
            m_dir = self.result_csv_file.parent / self.result_dir
            new_name = self.result_csv_file.name
            if self.setting_name and self.setting_value:
                new_name = f'rf2_{self.setting_name}_{self.setting_value}'

            m_dir.mkdir(exist_ok=True)
            shutil.move(self.result_csv_file, m_dir / new_name)
        except Exception as e:
            logging.error('Error moving result file: %s', e)
            return False
        return True

    def _index_fpsvr_csv_dir(self):
        if not self.fps_vr_cmd.exists():
            return

        for file in get_fpsvr_dir().glob('*.csv'):
            self.fpsvr_csv_index.add(file.name)

    def _get_fpsvr_cmd(self):
        s = SteamApps()
        path = s.find_game_location(FPSVR_APPID)

        if path and path.exists():
            self.fps_vr_cmd = path / 'fpsVRcmd.exe'
