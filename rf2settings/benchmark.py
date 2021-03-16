import logging
import shutil
import sys
import threading
from datetime import datetime
from pathlib import Path, WindowsPath
from queue import Queue, Empty
from subprocess import Popen
from time import time, sleep
from typing import Optional, Iterator, Tuple, Any, List

from rf2settings.preset.settings_model import BaseOptions
from rf2settings.globals import get_fpsvr_dir, FPSVR_APPID, get_present_mon_bin
from rf2settings.preset.preset import GraphicsPreset
from rf2settings.process import RunProcess
from rf2settings.rf2sharedmem import sharedMemoryAPI
from rf2settings.rfactor import RfactorPlayer
from rf2settings.valve.steam_utils import SteamApps


"""
base_url = 'localhost'
web_ui_port = 5397

Get replay dict: GET
/rest/watch/replays

Load and play replay: GET
/rest/watch/play/<replay_id>'

Switch to fullscreen: POST (with data=None)
/navigation/action/NAV_TO_FULL_EVENT_MONITOR

Quit the game: POST (with data=None)
/rest/start/quitGame
"""


class RunRfactorBenchmark:
    sim_info = None  # used to determine if track is loaded
    initial_loading_timeout = 30.0
    loading_timeout = 25.0
    benchmark_length = 60.0

    result_dir = 'benchdata'
    present_mon_bin = get_present_mon_bin()
    present_mon_result_dir: Path = get_fpsvr_dir() / 'rf2'

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
        self.kill_pm_event = threading.Event()
        self.rf = rf or RfactorPlayer(dev=True)

        # Prepare settings to be applied
        self.benchmark_preset = preset
        self.current_preset = GraphicsPreset()
        self.current_preset.update(self.rf)
        self.setting_name, self.setting_value = setting_name, setting_value

        self.fps_vr_cmd = Path('./fpsVRcmd.exe')
        self._get_fpsvr_cmd()

        # Keep an index of fpsVR csv files present before the current benchmark
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
                '+autotest', '-assert', '+skipmonitor', '+quickrace', '+grandprix', '+nosound', '-detectliveries',
                '+delayrender', '+skipoptions']
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

        # -- additional verify via rf2sharedmemory that we are on track
        """
        timeout_start = time()
        self.sim_info = sharedMemoryAPI.SimInfoAPI()
        logging.info('Verifying that track is loaded with rf2sharedmemory')
        while time() - timeout_start < (self.loading_timeout * 2):
            if self.sim_info.isSharedMemoryAvailable():
                if self.sim_info.isTrackLoaded():
                    logging.info('rf2sharedmemory detected that track is loaded')
                    break
            else:
                logging.debug('rf2sharedmemory not available')
            sleep(self.loading_timeout * 0.2)
        """

        # -- Start fpsVR logging
        self._index_fpsvr_csv_dir()
        self.start_stop_fpsvr_logging()

        # -- Start timed Present Mon logging
        p = None
        if not self.fps_vr_cmd.exists() and self.present_mon_bin.exists():
            cmd = self.present_mon_logging_cmd()
            logging.info('Running Present Mon: %s', cmd)
            p = RunProcess(cmd, cwd, self.kill_pm_event, stdout_q)
            p.start()

        # -- Wait for _benchmark_length_ seconds
        logging.info('rF Benchmark started logging.')
        while time() - timeout_start < self.benchmark_length:
            self.kill_event.wait(self.benchmark_length * 0.25)

        # -- Stop Benchmark
        self.start_stop_fpsvr_logging()
        self.close()
        logging.info('rF Benchmark stopped logging and will collect results.')
        sleep(1)  # Give fpsVR some time to write the results

        # -- Restore previous settings
        if self.benchmark_preset is not None:
            self.rf.write_settings(self.current_preset)

        # -- Collect and move fpsVR CSV results
        self._collect_fpsvr_result()
        self._write_fpsvr_result()

        # -- Join Present Mon Process
        if p is not None:
            p.join()
        logging.info('rF2 Benchmark Run finished.')

    def close(self):
        self.kill_event.set()
        self.kill_pm_event.set()

    def present_mon_logging_cmd(self) -> list:
        new_name = f'{datetime.now().strftime("%Y%m%d-%H-%M")}_{self.setting_name}_{self.setting_value}.csv'
        file = self.present_mon_result_dir / new_name
        if not self.present_mon_result_dir.exists():
            self.present_mon_result_dir.mkdir(exist_ok=True)

        cmd = ['-process_name', 'rFactor2 Mod Mode.exe', '-output_file', str(WindowsPath(file)),
               '-delay', '5', '-timed', str(int(self.benchmark_length)), '-no_top',
               '-dont_restart_as_admin', '-terminate_after_timed', '-stop_existing_session', '-terminate_existing',
               '-simple']
        return [self.present_mon_bin, ] + cmd

    def start_stop_fpsvr_logging(self):
        if not self.fps_vr_cmd.exists():
            return

        args = [self.fps_vr_cmd, 'logging_startstop']
        try:
            Popen(args)
        except Exception as e:
            logging.error('Error starting fpsVR frames logging: %s', e)

    def _collect_fpsvr_result(self):
        if not self.fps_vr_cmd.exists():
            return

        for file in get_fpsvr_dir().glob('*.csv'):
            if file.name not in self.fpsvr_csv_index:
                self.result_csv_file = file
                break

    def _write_fpsvr_result(self) -> bool:
        if not self.result_csv_file.exists() or not self.fps_vr_cmd.exists():
            return False

        try:
            m_dir = self.result_csv_file.parent / self.result_dir
            new_name = self.result_csv_file.name
            if self.setting_name and self.setting_value:
                new_name = f'rf2_{self.setting_name}_{self.setting_value}.csv'

            m_dir.mkdir(exist_ok=True)
            shutil.move(self.result_csv_file, m_dir / new_name)
            logging.info('Created fpsVR result file: %s', Path(m_dir / new_name).as_posix())
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
        if self.present_mon_bin.exists():
            return

        s = SteamApps()
        path = s.find_game_location(FPSVR_APPID)

        if path and path.exists():
            self.fps_vr_cmd = path / 'fpsVRcmd.exe'

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

    RunRfactorBenchmark.edit_preset_option(bench_preset, 'EPostProcessingSettings', 2)
    RunRfactorBenchmark.edit_preset_option(bench_preset, 'Shadows', 3)

    for setting in settings:
        key, name, value, value_name = setting

        # Adjust rF2 settings
        RunRfactorBenchmark.edit_preset_option(bench_preset, key, value)

        # Run the benchmark
        rb = RunRfactorBenchmark(preset=bench_preset, setting_name=name, setting_value=value_name or str(value))
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
