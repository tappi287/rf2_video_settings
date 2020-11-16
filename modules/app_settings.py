import logging
import sys
from pathlib import Path
from shutil import copyfile
import jsonpickle

from .globals import get_settings_dir, SETTINGS_FILE_NAME
from .rfactor import RfactorPlayer

jsonpickle.set_preferred_backend('json')
logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)


class AppSettings:
    backup_created = False
    selected_preset = 0

    def __init__(self):
        self.backup_created = AppSettings.backup_created
        self.selected_preset = AppSettings.selected_preset

    @staticmethod
    def create_backup(rf: RfactorPlayer):
        result = False
        files = (rf.player_file, rf.ini_file)

        for org in files:
            bak = org.with_suffix('.original')

            if AppSettings.backup_created and bak.exists():
                result = True
                continue

            try:
                copyfile(org, bak)
                result = True
            except Exception as e:
                logging.fatal('Could not back-up file: %s %s', org.as_posix(), e)
                result = False

        AppSettings.backup_created = result
        AppSettings.save()
        return result

    @staticmethod
    def _get_settings_file() -> Path:
        return get_settings_dir() / SETTINGS_FILE_NAME

    @classmethod
    def save(cls):
        try:
            with open(cls._get_settings_file().as_posix(), 'w') as f:
                f.write(jsonpickle.encode(AppSettings()))
        except Exception as e:
            logging.fatal('Could not save application settings! %s', e)
            return False
        return True

    @classmethod
    def load(cls) -> bool:
        try:
            with open(cls._get_settings_file().as_posix(), 'r') as f:
                settings = jsonpickle.decode(f.read())

                # - Restore class fields
                for k, v in settings.__dict__.items():
                    if k[:2] != '__':
                        if not callable(v):
                            setattr(AppSettings, k, v)
        except Exception as e:
            logging.fatal('Could not load application settings! %s', e)
            return False
        return True
