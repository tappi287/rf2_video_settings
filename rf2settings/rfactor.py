import json
import logging
import sys
from configparser import ConfigParser
from pathlib import Path
import subprocess
from typing import Optional, Iterator

from .globals import RFACTOR_PLAYER, RFACTOR_DXCONFIG, RF2_APPID, RFACTOR_VERSION_TXT, RFACTOR_CONTROLLER
from .preset.preset import BasePreset
from .preset.settings_model import BaseOptions, OptionsTarget
from .preset.settings_model_base import OPTION_CLASSES
from .valve.steam_utils import SteamApps

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)

"""
ModMgr.exe
HKEY_CURRENT_USER\\SOFTWARE\\Image Space Incorporated\\rFactor2 Mod Manager\\--guid--\\Packages Dir
File1
- key must point to Packages directory
"""


class RfactorLocation:
    path: Path = None
    player_json = Path()
    controller_json = Path()
    dx_config = Path()
    version_txt = Path()
    _app_id = RF2_APPID
    is_valid = False

    @classmethod
    def get_location(cls, dev: Optional[bool] = False):
        try:
            s = SteamApps()
        except Exception as e:
            logging.error('Error getting rFactor location: %s', e)
            return

        path = s.find_game_location(cls._app_id)
        if path and path.exists():
            player_json = path / RFACTOR_PLAYER
            controller_json = path / RFACTOR_CONTROLLER
            dx_config = path / RFACTOR_DXCONFIG
            version_txt = path / RFACTOR_VERSION_TXT

            if dev:
                player_json = path / 'ModDev' / RFACTOR_PLAYER
                controller_json = path / 'ModDev' / RFACTOR_CONTROLLER
                dx_config = path / 'ModDev' / RFACTOR_DXCONFIG

            if player_json.exists() and dx_config.exists():
                cls.is_valid = True
                cls.path = path
                cls.player_json = player_json
                cls.controller_json = controller_json
                cls.dx_config = dx_config
                cls.version_txt = version_txt


class RfactorPlayer:
    resolution_key = 'resolution_settings'
    config_parser_args = {'inline_comment_prefixes': '//', 'default_section': 'COMPONENTS'}

    class Options:
        def __init__(self):
            for field, base_cls in OPTION_CLASSES.items():
                options_instance = base_cls()
                setattr(self, field, options_instance)

    def __init__(self, dev: Optional[bool] = None, only_version: bool = False):
        self.dev = dev or False
        self.player_file = Path()
        self.controller_file = Path()
        self.ini_file = Path()
        self.ini_first_line = str()
        self.ini_config = self._create_ini_config_parser()
        self.location = Path('../modules')
        self.version_file = Path()
        self.version = ''

        self.options = self.Options()

        self.is_valid = False
        self.error = ''

        self.get_current_rfactor_settings(only_version)

    def get_current_rfactor_settings(self, only_version: bool = True):
        """ Read all settings from the current rFactor 2 installation """
        self._get_location()

        if not self._read_version():
            self.error += 'Could not read rFactor 2 version\n'
        if only_version:
            return

        # -- Read Player JSON
        player_json = self.read_player_json_dict(self.player_file, encoding='utf-8')
        # -- Get Options from Player JSON
        r = self._read_options_from_target(OptionsTarget.player_json, player_json)
        del player_json

        # -- Read Controller JSON
        controller_json = self.read_player_json_dict(self.controller_file, encoding='cp1252')
        r = self._read_options_from_target(OptionsTarget.controller_json, controller_json) and r
        del controller_json

        if not r:
            # -- Error reading either player or controller JSON
            return

        # -- Read dx_config
        config = self.read_dx_ini()
        if not config:
            self.is_valid = False
            return
        # -- Get Options from dx_config
        for preset_options in self._get_target_options(OptionsTarget.dx_config):
            if not self._get_options_from_dx_config(preset_options, config):
                self.error += f'Could not read rFactor2 CONFIG_DX11.ini for ' \
                              f'{preset_options.__class__.__name__}\n'
                self.is_valid = False
                return

        self.is_valid = True

    def _get_target_options(self, target: OptionsTarget, options=None) -> Iterator[BaseOptions]:
        if options is None:
            options = self.options

        for k, v in options.__dict__.items():
            if isinstance(v, BaseOptions):
                if v.target == target:
                    yield v

    def _read_options_from_target(self, target: OptionsTarget, json_dict) -> bool:
        for preset_options in self._get_target_options(target):
            if not self._get_options_from_player_json(preset_options, json_dict):
                self.error += f'Could not read rFactor2 settings for ' \
                              f'{preset_options.__class__.__name__}\n'
                self.is_valid = False
                return False
        return True

    def write_settings(self, preset: BasePreset) -> bool:
        """ Writes all settings of a preset into the rFactor 2 installation

        :param preset:
        :return:
        """
        # -- Write video config to dx_config
        self._write_video_config(preset)

        # -- Update Player Json settings
        player_json_dict = self.read_player_json_dict(self.player_file, encoding='utf-8')
        update_result = self._write_to_target(OptionsTarget.player_json, preset, player_json_dict)

        # -- Update Controller Json settings
        controller_json_dict = self.read_player_json_dict(self.controller_file, encoding='cp1252')
        update_result = self._write_to_target(
            OptionsTarget.controller_json, preset, controller_json_dict) and update_result

        if not update_result:
            return False

        # -- Write JSON files
        r = self.write_json(player_json_dict, self.player_file, encoding='utf-8')
        return r and self.write_json(controller_json_dict, self.controller_file, encoding='cp1252')

    def write_json(self, json_dict: dict, file: Path, encoding: str = 'UTF-8') -> bool:
        try:
            with open(file, 'w', encoding=encoding) as f:
                json.dump(json_dict, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.error += f'Error while writing file! {e}\n'
            logging.fatal(self.error)
            return False
        return True

    def _write_to_target(self, target: OptionsTarget, preset: BasePreset, json_dict: dict) -> bool:
        for preset_options in self._get_target_options(target, preset):
            if not self._update_player_json(json_dict, preset_options):
                return False
        return True

    def _write_video_config(self, preset: BasePreset):
        """ Update the Config_DX11.ini with supported Video Settings """
        settings_updated = False

        for preset_options in self._get_target_options(OptionsTarget.dx_config, preset):
            for option in preset_options.options:
                if option.key not in self.ini_config[self.ini_config.default_section]:
                    self.error += f'Could not locate settings key: {option.key} in CONFIG_DX11.ini\n'
                    logging.error(self.error)
                    continue
                if option.value is not None:
                    self.ini_config[self.ini_config.default_section][option.key] = str(option.value)
                    logging.info('Updated Dx Setting: %s: %s', option.key, option.value)
                    settings_updated = True

        if not settings_updated:
            logging.info('Found no updated Video Settings. Skipping update of dx_config!')
            return

        # -- Write Video Config.ini
        try:
            # - Write config
            with open(self.ini_file, 'w') as f:
                self.ini_config.write(f)

            # - Restore first ini comment line
            with open(self.ini_file, 'r') as f:
                f_lines = f.readlines()
            f_lines = [self.ini_first_line] + f_lines

            # - Remove trailing new line
            if f_lines[-1] == '\n':
                f_lines = f_lines[:-1]
            # - Remove trailing new line character
            f_lines[-1] = f_lines[-1].rstrip('\n')

            # - Remove spaced assign
            for idx, line in enumerate(f_lines):
                f_lines[idx] = line.replace(' = ', '=')

            # - Write modified config
            with open(self.ini_file, 'w') as f:
                f.writelines(f_lines)
        except Exception as e:
            self.error += f'Could not write CONFIG_DX11.ini file! {e}\n'
            logging.error(self.error)
            return False

    def _update_player_json(self, player_json_dict, preset_options: BaseOptions):
        if preset_options.key not in player_json_dict:
            self.error += f'Could not locate CATEGORY settings key: {preset_options.key} in player.JSON.\n'
            logging.error(self.error)
            return False

        for option in preset_options.options:
            if option.key in preset_options.skip_keys:
                continue
            if option.key not in player_json_dict[preset_options.key]:
                logging.warning('Skipping Setting: %s in player.JSON that could not be located!', option.key)
                continue
            if option.value is None:
                logging.debug('Skipping write of %s because value is None.', option.key)
                continue

            player_json_dict[preset_options.key][option.key] = option.value
            logging.info('Updated Setting: %s: %s', option.key, option.value)

        return True

    def _get_options_from_dx_config(self, video_settings: BaseOptions, config: ConfigParser) -> bool:
        if not config:
            return False
        self.ini_config = config
        config_dict = self.ini_config[self.ini_config.default_section]

        settings_updated = False
        for option in video_settings.options:
            if option.key not in config_dict:
                continue
            value = config_dict.get(option.key)
            if option.ini_type is int:
                value = int(value)
            option.value = value
            settings_updated = True

        return settings_updated

    @staticmethod
    def _get_options_from_player_json(preset_options: BaseOptions, player_json: dict) -> bool:
        if not player_json:
            return False

        settings_updated = False
        player_graphic_options = player_json.get(preset_options.key)
        for option in preset_options.options:
            if option.key not in player_graphic_options:
                continue
            option.value = player_graphic_options.get(option.key)
            settings_updated = True

        return settings_updated

    def read_player_json_dict(self, file: Path, encoding: Optional[str] = None) -> Optional[dict]:
        try:
            with open(file, 'r', encoding=encoding) as f:
                return json.load(f)
        except Exception as e:
            msg = f'Could not read {file.name} file! {e}'
            logging.fatal(msg)
            self.error += f'{msg}\n'

    def read_dx_ini(self) -> Optional[ConfigParser]:
        try:
            conf = self._create_ini_config_parser()
            with open(self.ini_file, 'r') as f:
                self.ini_first_line = f.readline()
                conf.read_file(f)
                return conf
        except Exception as e:
            self.error += f'Could not read CONFIG_DX11.ini file! {e} {self.ini_file}\n'
            logging.fatal(self.error)

    def _read_version(self) -> bool:
        if not self.version_file.exists():
            return False
        try:
            with open(self.version_file, 'r') as f:
                self.version = f.readline()
        except Exception as e:
            logging.error('Error reading version file: %s', e)
            return False

        return True

    def _create_ini_config_parser(self):
        config_parser = ConfigParser(**self.config_parser_args)
        config_parser.optionxform = str
        return config_parser

    def _get_location(self):
        if not RfactorLocation.is_valid:
            RfactorLocation.get_location(self.dev)
            self.error += f'rFactor 2 installation detected at {RfactorLocation.path}\n'
        if not RfactorLocation.is_valid:
            self.error += 'Could not locate rFactor 2 installation\n'
            return

        self.location = RfactorLocation.path
        self.player_file = RfactorLocation.player_json
        self.controller_file = RfactorLocation.controller_json
        self.ini_file = RfactorLocation.dx_config
        self.version_file = RfactorLocation.version_txt

    def _check_bin_dir(self) -> bool:
        return self.location and Path(self.location / 'Bin64').exists()

    def run_rfactor(self, server_info: Optional[dict] = None) -> bool:
        if not self._check_bin_dir():
            self.error += 'Could not locate rFactor 2 Bin directory.\n'
            return False

        # Solution for non loading rF2 plugins in PyInstaller executable:
        #    ctypes.windll.kernel32.SetDllDirectoryA(None)
        # See https://github.com/pyinstaller/pyinstaller/wiki/Recipe-subprocess#windows-dll-loading-order

        executable = self.location / "Bin64" / "rFactor2.exe"
        cmd = [executable]

        if server_info:
            ip, port = server_info.get('address', ('localhost',))[0], server_info.get('port', '64297')
            p = server_info.get('password')
            cmd += ['+multiplayer', f'+connect={":" if p else ""}{p}{"@" if p else ""}{ip}:{port}']

        logging.info('Launching %s', cmd)

        subprocess.Popen(cmd, cwd=self.location)

        return True

    def run_config(self) -> bool:
        if not self._check_bin_dir():
            return False

        executable = self.location / "Bin64" / "rF Config.exe"
        p = subprocess.Popen(executable, cwd=self.location, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             stdin=subprocess.PIPE)
        out, errs = p.communicate()
        if p.returncode != 0:
            self.error += str(out, encoding='utf-8')
            return False

        return True
