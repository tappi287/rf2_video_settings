import json
import logging
import sys
from pathlib import Path, WindowsPath
from shutil import copyfile
from typing import Iterator, Union

from .presets_dir import PresetDir, get_user_presets_dir
from .utils import JsonRepr
from .globals import get_settings_dir, SETTINGS_FILE_NAME, get_default_presets_dir
from .rfactor import RfactorPlayer

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)


class AppSettings(JsonRepr):
    backup_created = False
    needs_admin = False
    selected_preset = str()
    user_presets_dir = str()
    deleted_defaults = list()  # Default Presets the user deleted

    def __init__(self):
        self.backup_created = AppSettings.backup_created
        self.selected_preset = AppSettings.selected_preset
        self.user_presets_dir = AppSettings.user_presets_dir

    @staticmethod
    def update_user_presets_dir(user_presets_dir: Union[str, Path]) -> bool:
        user_presets_dir = Path(user_presets_dir)
        user_presets_dir_str = str(WindowsPath(user_presets_dir))

        try:
            if user_presets_dir.exists():
                logging.info('Updating User Presets Dir: %s', user_presets_dir_str)
                PresetDir.value = user_presets_dir_str
                AppSettings.user_presets_dir = user_presets_dir_str
                AppSettings.save()
                AppSettings.copy_default_presets()
            else:
                logging.error('Selected Presets Directory does not exist: %s', user_presets_dir.as_posix())
                return False
        except Exception as e:
            logging.error('Error accessing path: %s', e)
            return False

        return True

    @staticmethod
    def create_backup(rf: RfactorPlayer):
        result = False
        files = (rf.player_file, rf.ini_file)
        has_permission_error = False

        for org in files:
            if not org.is_file():
                continue

            bak = org.with_suffix('.original')

            if AppSettings.backup_created and bak.exists():
                result = True
                continue

            try:
                copyfile(org, bak)
                result = True
            except Exception as e:
                if type(e) is PermissionError:
                    has_permission_error = True

                logging.fatal('Could not back-up file: %s %s', org.as_posix(), e)
                result = False

        if has_permission_error:
            logging.error('Accessing rf2 files requires Admin rights!')
            AppSettings.needs_admin = True

        AppSettings.backup_created = result
        AppSettings.save()
        return result

    @staticmethod
    def iterate_default_presets() -> Iterator[Path]:
        for file in get_default_presets_dir().glob('*.json'):
            yield file

    @classmethod
    def copy_default_presets(cls) -> bool:
        result = False

        for file in cls.iterate_default_presets():
            dst = get_user_presets_dir() / file.name
            if dst.exists() or file.stem in cls.deleted_defaults:
                continue

            try:
                copyfile(file, dst.with_name(file.name))
                result = True
            except Exception as e:
                logging.error('Could not copy default preset: %s', e)
                result = False

        return result

    @staticmethod
    def _get_settings_file() -> Path:
        return get_settings_dir() / SETTINGS_FILE_NAME

    @classmethod
    def save(cls):
        try:
            with open(cls._get_settings_file().as_posix(), 'w') as f:
                js_dict = dict()
                for k, v in cls.__dict__.items():
                    if k[:2] != '__' and isinstance(v, (bool, str, list, dict)):
                        js_dict[k] = v
                f.write(json.dumps(js_dict))
        except Exception as e:
            logging.fatal('Could not save application settings! %s', e)
            return False
        return True

    @classmethod
    def load(cls) -> bool:
        try:
            with open(cls._get_settings_file().as_posix(), 'r') as f:
                settings = json.loads(f.read())

                # - Restore class fields
                for k, v in settings.items():
                    if k[:2] != '__' and not callable(v):
                        setattr(AppSettings, k, v)
        except Exception as e:
            logging.fatal('Could not load application settings! %s', e)
            return False

        # -- Setup custom user preset dir if set --
        PresetDir.value = AppSettings.user_presets_dir
        return True
