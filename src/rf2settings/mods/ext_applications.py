import logging
import subprocess
from pathlib import WindowsPath
from typing import Optional

import psutil

from rf2settings.valve.steam_utils import SteamApps

ARGS_MAPPING = {"kneeboard": None, "crew_chief": ["-game", "RF2", "-skip_updates"], "sim_hub": None}


def is_application_running(app_executable_name: str) -> bool:
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"].lower().startswith(app_executable_name.lower()):
            return True
    return False


def _start_application(app_bin_path: WindowsPath = None, args: Optional[list] = None):
    if not app_bin_path or not app_bin_path.exists():
        return

    if is_application_running(app_bin_path.name):
        logging.debug(f"{app_bin_path.name} is already running")
        return

    if args is not None:
        cmds = [app_bin_path, *args]
    else:
        cmds = app_bin_path

    process = subprocess.Popen(cmds, cwd=app_bin_path.parent, creationflags=subprocess.DETACHED_PROCESS)
    logging.info(f"{app_bin_path.name} process started with PID: {process.pid}")


def _get_steam_apps_known_app(app_key: str) -> dict:
    s = SteamApps()
    if not s.known_apps:
        s.read_steam_library()
    return s.known_apps.get(app_key)


def get_app_executable_path(app_key: str) -> Optional[WindowsPath]:
    known_apps_entry = _get_steam_apps_known_app(app_key)
    if known_apps_entry:
        path = WindowsPath(known_apps_entry.get("installdir") or str())
        executable_sub_path = known_apps_entry.get("exe_sub_path", "")
        if executable_sub_path:
            executable_path = path / executable_sub_path / known_apps_entry.get("executable", "")
        else:
            executable_path = path.joinpath(known_apps_entry.get("executable", ""))
        if executable_path.is_file():
            return executable_path
    return None


def start_application(app_key: str):
    args = ARGS_MAPPING.get(app_key, None)
    app_bin_path = get_app_executable_path(app_key)
    _start_application(app_bin_path, args)
