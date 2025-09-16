import logging
import re
from datetime import datetime
from pathlib import Path

from rf2settings.rfactor import RfactorPlayer
from rf2settings.utils import create_file_safe_name

REPLAY_FILE_SUFFIX = ".Vcr"
RESULT_FILE_SUFFIX = ".xml"
RESULT_TIME_THRESHOLD = 180.0 * 4  # 60s * 4


def get_replay_location_from_rfactor_player(rf: RfactorPlayer) -> Path:
    if hasattr(rf.options, "game_options"):
        option = rf.options.game_options.get_option("Custom Replay Folder")
        if option and option.value:
            return Path(option.value)

    return rf.location / 'UserData' / 'Replays'


def get_replays_location() -> Path | None:
    rf = RfactorPlayer()
    if not rf.is_valid:
        return

    return get_replay_location_from_rfactor_player(rf)


def get_result_location_from_rfactor_player(rf: RfactorPlayer) -> Path | None:
    user_data_path = rf.player_file.parents[1]
    return user_data_path.joinpath("Log/Results")


def rename_replay(replay: dict, new_name: str, replay_location: Path | None = None):
    try:
        p: Path = replay_location or get_replays_location()
        replay_file: Path = p / f"{replay.get('name', '')}{REPLAY_FILE_SUFFIX}"
        target_file = replay_file.with_stem(create_file_safe_name(new_name, allow_spaces=True))
        replay_file.rename(target_file)
        logging.info("Renaming replay: %s to %s", replay.get("name"), target_file.as_posix())
        return True
    except Exception as e:
        logging.error("Error renaming replay: %s", e)

    return False


def delete_replays(replays: list, replay_location: Path | None = None):
    errors = list()
    p: Path = replay_location or get_replays_location()

    for r in replays:
        try:
            replay_file: Path = p / f"{r.get('name', '')}{REPLAY_FILE_SUFFIX}"
            if replay_file.exists():
                logging.debug("Deleting replay: %s", replay_file.as_posix())
                replay_file.unlink()
        except Exception as e:
            logging.error("Error deleting replay: %s", e)
            errors.append(f"Error deleting replay: {e}")

    if errors:
        return False, errors
    return True, list()


def create_result_files_lookup(result_location: Path) -> dict[str, list[dict[Path, float]]]:
    """Store Result Files in groups within same hour

    Example:
    2010-01-01-13(hour) Store all files for 01.01.2010 1pm
    {"2010010113": [{"path": Path("File.xml"), "m_time": 123.0}]

    """
    result_files = dict()
    for f in result_location.glob(f"*{RESULT_FILE_SUFFIX}"):
        m_time = f.stat().st_mtime
        timestamp_group = datetime.fromtimestamp(m_time).strftime("%Y%m%d%H")
        if timestamp_group not in result_files:
            result_files[timestamp_group] = list()
        result_files[timestamp_group].append({"path": f, "m_time": m_time})

    return result_files


def match_result_file_to_replay(replay_file_stats, result_files: dict[str, list[dict[Path, float]]]) -> str:
    """Find matching result files, written within the same seconds/time threshold"""
    timestamp_group = datetime.fromtimestamp(replay_file_stats.st_mtime).strftime("%Y%m%d%H")
    result_file = str()

    if timestamp_group not in result_files:
        return result_file

    # Get file candidates within the same hour
    # and store them by their timedelta to the replay file
    candidates = {abs(r.get("m_time") - replay_file_stats.st_mtime): r for r in result_files[timestamp_group]}
    if not candidates:
        return result_file

    # Match the file candidate with the lowest delta to replay file modified date
    delta, result_entry = sorted(candidates.items())[0]
    # Make sure time delta is within threshold
    if delta < RESULT_TIME_THRESHOLD:
        result_file = result_entry["path"].as_posix()

    return result_file


def get_replays(rf: RfactorPlayer | None = None) -> list[dict]:
    """Return attributes of all replays as JSON ready list sorted by date"""
    result_location, result_files = None, dict()
    if rf is None:
        rf = RfactorPlayer()
        p = get_replay_location_from_rfactor_player(rf)
        result_location = get_result_location_from_rfactor_player(rf)
    else:
        p = get_replay_location_from_rfactor_player(rf)
        result_location = get_result_location_from_rfactor_player(rf)

    if result_location is not None and result_location.exists():
        result_files = create_result_files_lookup(result_location)

    replays = list()

    for idx, r in enumerate(p.glob(f"*{REPLAY_FILE_SUFFIX}")):
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

        result_file = match_result_file_to_replay(s, result_files)

        # define Entry
        replay = {
            "id": idx,
            "name": r.stem,
            "size": f"{s.st_size / 1048576:.2f}MB",
            "result_file": result_file,
            "ctime": s.st_mtime,
            "type": replay_type,
            "date": datetime.fromtimestamp(s.st_mtime).strftime("%Y-%m-%d %H:%M"),
        }
        replays.append(replay)

    return sorted(replays, key=lambda e: e["ctime"], reverse=True)
