import logging
import subprocess
from datetime import datetime

import time
from pathlib import Path

from rf2settings.globals import get_fpsvr_dir, FPSVR_APPID
from rf2settings.valve.steam_utils import SteamApps


class FpsVR:
    FRAMETIMES_FILE_PREFIX = 'Frametimes#'
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
        self.result_details_csv_file = Path()
        self.target_result_name = target_result_name

    def start(self) -> bool:
        """ Run the benchmark for _benchmark_length_ seconds. """
        # -- Start fpsVR logging
        self._index_fpsvr_csv_dir()
        result = self.start_stop_fpsvr_logging()

        # -- Wait for _benchmark_length_ seconds
        logging.info('rF Benchmark started logging.')
        return result

    def stop(self) -> bool:
        # -- Stop Benchmark
        if self.start_stop_fpsvr_logging():
            logging.info('FPS VR stopped logging and will collect results.')
            time.sleep(2)  # Give fpsVR some time to write the results
            self._collect_result()
            return True
        return False

    def start_stop_fpsvr_logging(self) -> bool:
        if not self.fps_vr_cmd.exists():
            return False

        args = [self.fps_vr_cmd, 'logging_startstop']
        try:
            subprocess.Popen(args)
        except Exception as e:
            logging.error('Error starting fpsVR frames logging: %s', e)
            return False
        return True

    def get_result_file(self):
        if self.result_csv_file and self.result_csv_file.is_file():
            return self.result_csv_file

    def _collect_result(self):
        if not self.fps_vr_cmd.exists():
            return

        for file in get_fpsvr_dir().glob('*.csv'):
            if file.name not in self.fpsvr_csv_index:
                self.result_csv_file = file

        # -- Rename result file
        if self.result_csv_file.exists() and self.result_csv_file.is_file() and self.target_result_name:
            target_path = self.result_csv_file.with_stem(
                f'{self.target_result_name}_{datetime.strftime(datetime.now(), "%Y-%m-%dT%H%M%S")}'
            )
            self.result_csv_file.rename(target_path)
            self.result_csv_file = target_path

    def _index_fpsvr_csv_dir(self):
        if not self.fps_vr_cmd.exists():
            return

        for file in get_fpsvr_dir().glob('*.csv'):
            self.fpsvr_csv_index.add(file.name)

    def _get_fpsvr_cmd(self):
        if self.fps_vr_cmd.exists() and self.fps_vr_cmd.is_file() and self.fps_vr_cmd.name == self.FPS_VR_CMD_EXE:
            return

        s = SteamApps()
        s.read_steam_library()
        path = s.find_game_location(FPSVR_APPID)

        if path and path.exists():
            self.fps_vr_cmd = path / self.FPS_VR_CMD_EXE
