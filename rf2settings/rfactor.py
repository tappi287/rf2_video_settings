import json
import logging
import sys
from configparser import ConfigParser
from pathlib import Path
from subprocess import Popen
from typing import Optional

from .globals import RFACTOR_PLAYER, RFACTOR_DXCONFIG, RF2_APPID, RFACTOR_VERSION_TXT
from .preset import Preset
from .settings_model import GraphicOptions, AdvancedGraphicSettings, VideoSettings, BaseOptions
from .valve.steam_utils import SteamApps

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)


class RfactorLocation:
    path: Path = None
    player_json = Path()
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
            dx_config = path / RFACTOR_DXCONFIG
            version_txt = path / RFACTOR_VERSION_TXT

            if dev:
                player_json = path / 'ModDev' / RFACTOR_PLAYER
                dx_config = path / 'ModDev' / RFACTOR_DXCONFIG

            if player_json.exists() and dx_config.exists():
                cls.is_valid = True
                cls.path = path
                cls.player_json = player_json
                cls.dx_config = dx_config
                cls.version_txt = version_txt


class RfactorPlayer:
    config_parser_args = {'inline_comment_prefixes': '//', 'default_section': 'COMPONENTS'}

    def __init__(self, dev: Optional[bool] = None, only_version: bool = False):
        self.dev = dev or False
        self.player_file = Path()
        self.ini_file = Path()
        self.ini_first_line = str()
        self.ini_config = self._create_ini_config_parser()
        self.location = Path('../modules')
        self.version_file = Path()
        self.version = ''

        self.graphic_options = GraphicOptions()
        self.advanced_graphic_options = AdvancedGraphicSettings()
        self.video_settings = VideoSettings()

        self.is_valid = False
        self.error = ''

        self.get_current_rfactor_settings(only_version)

    def _create_ini_config_parser(self):
        config_parser = ConfigParser(**self.config_parser_args)
        config_parser.optionxform = str
        return config_parser

    def get_current_rfactor_settings(self, only_version: bool = True):
        """ Read all settings from the current rFactor 2 installation """
        self._get_location()

        if not self._update_version():
            self.error += 'Could not read rFactor 2 version'
        if only_version:
            return

        for preset_options in (self.graphic_options, self.advanced_graphic_options):
            if not self._update_settings_from_player_json(preset_options):
                self.error = 'Could not read rFactor2 player.JSON'
                self.is_valid = False
                return

        if not self._update_settings_from_dx_config():
            self.error = 'Could not read rFactor2 CONFIG_DX11.ini'
            self.is_valid = False
            return

        self.is_valid = True

    def write_settings(self, preset: Preset) -> bool:
        """ Writes all settings of a preset into the rFactor 2 installation

        :param preset:
        :return:
        """
        # -- Write Video Config.ini
        for option in preset.video_settings.options:
            if option.key not in self.ini_config[self.ini_config.default_section]:
                self.error = f'Could not locate settings key: {option.key} in CONFIG_DX11.ini'
                logging.error(self.error)
                continue
            self.ini_config[self.ini_config.default_section][option.key] = str(option.value)

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
            self.error = f'Could not write CONFIG_DX11.ini file! {e}'
            logging.error(self.error)
            return False

        # -- Update Player Json settings
        update_result = True
        player_json_dict = self.get_player_json_dict()
        for preset_options in (preset.graphic_options, preset.advanced_graphic_options):
            if not self._update_player_json(player_json_dict, preset_options):
                update_result = False

        if not update_result:
            return False

        # -- Write Player JSON
        try:
            with open(self.player_file, 'w') as f:
                json.dump(player_json_dict, f, indent=4)
        except Exception as e:
            self.error = f'Error while writing player.JSON! {e}'
            logging.fatal(self.error)
            return False
        return True

    def _update_player_json(self, player_json_dict, preset_options: BaseOptions):
        if preset_options.key not in player_json_dict:
            self.error = f'Could not locate settings key: {preset_options.key} in player.JSON.'
            logging.error(self.error)
            return False

        for option in preset_options.options:
            if option.key not in player_json_dict[preset_options.key]:
                logging.warning('Skipping Setting: %s in player.JSON that could not be located!', option.key)
                continue
            player_json_dict[preset_options.key][option.key] = option.value
            logging.info('Updated Setting: %s: %s', option.key, option.value)

        return True

    def get_player_json_dict(self) -> Optional[dict]:
        try:
            with open(self.player_file, 'rb') as f:
                return json.load(f)
        except Exception as e:
            logging.fatal('Could not read player.JSON file! %s %s', e, self.player_file)

    def get_dx_ini(self) -> Optional[ConfigParser]:
        try:
            conf = self._create_ini_config_parser()
            with open(self.ini_file, 'r') as f:
                self.ini_first_line = f.readline()
                conf.read_file(f)
                return conf
        except Exception as e:
            logging.fatal('Could not read CONFIG_DX11.ini file! %s %s', e, self.ini_file)

    def _update_settings_from_dx_config(self) -> bool:
        config = self.get_dx_ini()
        if not config:
            return False
        self.ini_config = config
        config_dict = self.ini_config[self.ini_config.default_section]

        settings_updated = False
        for option in self.video_settings.options:
            if option.key not in config_dict:
                continue
            value = config_dict.get(option.key)
            if option.ini_type is int:
                value = int(value)
            option.value = value
            settings_updated = True

        return settings_updated

    def _update_settings_from_player_json(self, preset_options: BaseOptions) -> bool:
        player_json = self.get_player_json_dict()
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

    def _update_version(self) -> bool:
        if not self.version_file.exists():
            return False
        try:
            with open(self.version_file, 'r') as f:
                self.version = f.readline()
        except Exception as e:
            logging.error('Error reading version file: %s', e)
            return False

        return True

    def _get_location(self):
        if not RfactorLocation.is_valid:
            RfactorLocation.get_location(self.dev)
        if not RfactorLocation.is_valid:
            self.error = 'Could not locate rFactor 2 installation'
            return

        self.location = RfactorLocation.path
        self.player_file = RfactorLocation.player_json
        self.ini_file = RfactorLocation.dx_config
        self.version_file = RfactorLocation.version_txt

    def _check_bin_dir(self) -> bool:
        return self.location and Path(self.location / 'Bin64').exists()

    def run_rfactor(self, server_info: Optional[dict] = None) -> bool:
        if not self._check_bin_dir():
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

        Popen(cmd, cwd=self.location)

        return True

    def run_config(self) -> bool:
        if not self._check_bin_dir():
            return False
        executable = self.location / "Bin64" / "rF Config.exe"
        Popen(executable, cwd=self.location)
        return True
