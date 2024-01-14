import json
import logging
from pathlib import Path, WindowsPath
from shutil import copyfile
from typing import Iterator, Union, Dict

from .globals import get_settings_dir, SETTINGS_FILE_NAME, SETTINGS_CONTENT_FILE_NAME, get_default_presets_dir
from .globals import get_present_mon_bin
from .preset.preset_base import PRESET_TYPES
from .preset.presets_dir import PresetDir, get_user_presets_dir
from .rfactor import RfactorPlayer, RfactorLocation
from .utils import JsonRepr


class AppSettings(JsonRepr):
    backup_created = False
    needs_admin = False
    selected_presets: Dict[str, str] = dict()
    replay_preset = str()
    app_preferences = dict()

    rf_overwrite_location = ''

    # 1128 webui change
    # apiendpoints: http://localhost:5397/swagger/index.html
    last_rf_version = str()
    user_presets_dir = str()
    deleted_defaults = list()  # Default Presets the user deleted
    server_favourites = list()
    custom_servers = dict()
    server_browser: dict = {'filter_fav': False, 'filter_empty': False, 'filter_pwd': False, 'filter_version': False,
                            'filter_text': '', 'store_pwd': False}
    benchmark_settings = dict()
    chat_settings = list()
    yt_livestream: dict = None
    yt_channel_id = dict()
    headlight_settings = dict()
    headlight_controller_assignments = dict()
    headlight_rf_key = 'DIK_H'
    server_passwords = dict()
    apply_webui_settings = False
    controller_devices = dict()
    last_launch_method = None

    chat_plugin_version = {
        "458bca4acdd558539ff62fc2524cff71": "2022.10.18",
        "2022.10.19": "AIzaSyCGCHIx0WVbRlhQwuacQvBnuJQgxn8xwnE",
        "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": "2022.10.20",
        "f62fc2524cff71458bca4acdd558539f": "2022.10.23"
    }

    # -----------------------------------
    # -- Won't be saved to file:
    skip_keys = ['first_load_complete', 'session_selection', 'replay_playing',
                 'present_mon_bin', 'present_mon_result_dir', 'chat_plugin_version',
                 'content_selected', 'content_keys', 'content_urls', 'content', 'content_saved',
                 'yt_livestream', 'yt_channel_id']

    present_mon_bin: Path = get_present_mon_bin()
    present_mon_result_dir: Path = get_user_presets_dir() / 'benchmark_results'

    first_load_complete = False
    replay_playing = False

    content = dict()
    content_keys = ['series', 'tracks', 'cars']
    content_urls = ['/rest/race/series', '/rest/race/track', '/rest/race/car']

    content_selected = dict()   # Content Selection will be saved to preset but transferred to greenlets via this var
    session_selection = dict()  # Session Selection will be saved to preset but transferred to greenlets via this var
    content_saved = False

    def __init__(self):
        self.backup_created = AppSettings.backup_created
        self.selected_presets = AppSettings.selected_presets
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
        files = (rf.player_file, rf.controller_file, rf.ini_file, rf.ini_vr_file)
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
    def restore_backup(rf: RfactorPlayer):
        result = False
        files = (rf.player_file, rf.controller_file, rf.ini_file, rf.ini_vr_file)
        has_permission_error = False

        for org in files:
            if not org.is_file():
                continue

            bak = org.with_suffix('.original')

            if not bak.exists():
                logging.fatal('Could not locate BackUp file: %s', bak.as_posix())
                continue

            try:
                # Delete current file
                org.unlink()
                # Create original file
                copyfile(bak, org)
                result = True
            except Exception as e:
                if type(e) is PermissionError:
                    has_permission_error = True
                logging.fatal('Could not restore file: %s %s', org.as_posix(), e)
                result = False

        if has_permission_error:
            logging.error('Accessing rf2 files requires Admin rights!')
            AppSettings.needs_admin = True

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

            # -- Remove existing legacy default presets
            cls.delete_legacy_default_presets(dst)

            if dst.exists() or file.stem in cls.deleted_defaults:
                continue

            try:
                logging.info('Creating default preset: %s', file.name)
                copyfile(file, dst.with_name(file.name))
                result = True
            except Exception as e:
                logging.error('Could not copy default preset: %s', e)
                result = False

        return result

    @staticmethod
    def delete_current_settings_presets():
        """ Delete 'Current_Settings__Nickname' Presets so we can handle changed Usernames """
        for file in Path(AppSettings.user_presets_dir).glob('*.json'):
            for prefix in (p.prefix for p in PRESET_TYPES.values()):
                name = f'{prefix}_Current_Settings__'
                if file.stem.startswith(name):
                    try:
                        file.unlink(missing_ok=True)
                    except Exception as e:
                        logging.error('Error deleting current settings preset: %s', e)

    @staticmethod
    def delete_legacy_default_presets(dst: Path):
        """ Wipe pre 0.7.8 default Presets without prefixes """
        folder = dst.parent

        for prefix in (p.prefix for p in PRESET_TYPES.values()):
            legacy_preset_name = dst.name.removeprefix(f'{prefix}_')
            legacy_file = folder / legacy_preset_name
            if legacy_file.exists() and legacy_file != dst:
                logging.info('Deleting legacy preset: %s', legacy_file)
                legacy_file.unlink(missing_ok=True)

    @staticmethod
    def _get_settings_file() -> Path:
        return get_settings_dir() / SETTINGS_FILE_NAME

    @staticmethod
    def _get_settings_content_file() -> Path:
        return get_settings_dir() / SETTINGS_CONTENT_FILE_NAME

    @classmethod
    def save_content(cls):
        file = cls._get_settings_content_file()

        try:
            with open(file.as_posix(), 'w') as f:
                f.write(json.dumps(cls.content))
        except Exception as e:
            logging.error('Could not save content! %s', e)
            return False

        cls.content_saved = True
        return True

    @classmethod
    def save(cls, save_content: bool = False):
        # -- Save 'content' in separate file
        if cls.content and not cls.content_saved:
            cls.save_content()

        file = cls._get_settings_content_file() if save_content else cls._get_settings_file()

        try:
            with open(file.as_posix(), 'w') as f:
                if not save_content:
                    # -- Save Settings
                    # noinspection PyTypeChecker
                    f.write(json.dumps(cls.to_js_object(cls)))
                else:
                    # -- Save Content
                    f.write(json.dumps(cls.content))
        except Exception as e:
            logging.error('Could not save application settings! %s', e)
            return False
        return True

    @classmethod
    def _first_load(cls):
        if not cls.first_load_complete:
            # -- Reset Content data if rFactor version changed
            version = RfactorPlayer(only_version=True).version.replace('\n', '')
            logging.debug('Compared last known rF version %s with current version %s', cls.last_rf_version, version)

            if version != cls.last_rf_version:
                cls.last_rf_version = version
                content_data_file = cls._get_settings_content_file()
                if content_data_file.exists():
                    logging.info('Found differing rFactor version. Deleting content data.')
                    content_data_file.unlink()
                # -- Save updated version
                cls.save()
            else:
                cls.load_content()

            cls.first_load_complete = True

    @classmethod
    def load_content(cls) -> bool:
        file = cls._get_settings_content_file()

        try:
            if file.exists():
                with open(file.as_posix(), 'r') as f:
                    cls.content = json.loads(f.read())
        except Exception as e:
            logging.error('Could not load content list! %s', e)
            return False

        return True

    @classmethod
    def load(cls) -> bool:
        file = cls._get_settings_file()

        try:
            if file.exists():
                with open(file.as_posix(), 'r') as f:
                    # -- Load Settings
                    # noinspection PyTypeChecker
                    cls.from_js_dict(cls, json.loads(f.read()))
        except Exception as e:
            logging.error('Could not load application settings! %s', e)
            return False

        # -- Setup custom user preset dir if set --
        PresetDir.value = AppSettings.user_presets_dir

        # -- Overwrite rf2 location if overwrite location set
        if cls.rf_overwrite_location and cls.rf_overwrite_location not in ('.', '..', '../modules'):
            RfactorLocation.overwrite_location(cls.rf_overwrite_location)
            logging.info(f'Using rF2 overwrite location: {RfactorLocation.path}')

        # -- Operations on first load
        cls._first_load()

        return True

    @classmethod
    def update_webui_settings(cls, rf: RfactorPlayer):
        # -- Update WebUi Session Settings for next run
        if rf.webui_session_settings:
            cls.session_selection = rf.webui_session_settings
        # -- Update WebUi Content Selection Settings for next run
        if rf.webui_content_selection:
            cls.content_selected = rf.webui_content_selection
