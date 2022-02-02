import logging
from pathlib import Path
from typing import Iterator, Union, Type

from open_vr_mod.mod import FsrMod, FoveatedMod
from rf2settings.preset.settings_model import BaseOptions


class OpenVrMod:
    def __init__(self, options: Iterator[BaseOptions], location: Path,
                 mod_type: Union[Type[FsrMod], Type[FoveatedMod]]):
        self.options = options
        rf_manifest = {
            'path': location.as_posix(),
            FsrMod.DLL_LOC_KEY: [Path(location / 'Bin64' / 'openvr_api.dll').as_posix()],
            FsrMod.DLL_LOC_KEY_SELECTED: [Path(location / 'Bin64' / 'openvr_api.dll').as_posix()],
        }
        self.mod = mod_type(rf_manifest)
        self.error = str()

    def _update_mod_config_from_preset(self) -> bool:
        use_mod = False
        js_settings_ls = list()

        for preset_options in self.options:
            for option in preset_options.options:
                parent, key = None, option.key
                if len(key.split(' ')) > 1:
                    parent, key = key.split(' ', 1)

                if parent is None and key == 'enabled':
                    use_mod = option.value

                js_settings_ls.append(
                    {'key': key, 'parent': parent, 'value': option.value}
                )

        self.mod.settings.from_js_dict(js_settings_ls)
        return use_mod

    def _update_preset_from_mod_config(self) -> bool:
        result = self.mod.update_from_disk()
        if not result:
            self.error = self.mod.error

        mod_settings = self.mod.settings.to_dict()
        if not result:
            mod_settings['enabled']['value'] = False

        for preset_options in self.options:
            for option in preset_options.options:
                mod_setting = mod_settings.get(option.key)
                if not mod_setting:
                    continue
                option.value = mod_setting.get('value')
                option.exists_in_rf = True

        return result

    def write(self) -> bool:
        # -- Update mod install state
        self.mod.update_from_disk()
        mod_installed = self.mod.manifest[self.mod.VAR_NAMES['installed']]

        # -- Update Mod Settings from Preset
        use_mod = self._update_mod_config_from_preset()

        result = False
        match mod_installed:
            case False if use_mod:
                # -- Install
                logging.info('Installing OpenVR Mod %s', self.mod.__class__.__name__)
                result = self.mod.install(uninstall=False)
            case True if use_mod:
                # -- Update Mod Settings
                logging.info('Updating OpenVR Mod %s configuration', self.mod.__class__.__name__)
                result = self.mod.write_updated_cfg()
            case True if not use_mod:
                # -- Uninstall
                logging.info('Uninstalling OpenVR Mod %s', self.mod.__class__.__name__)
                result = self.mod.install(uninstall=True)

        if self.mod.error:
            self.error = self.mod.error

        return result

    def read(self) -> bool:
        logging.debug('Reading OpenVR Mod settings for %s', self.mod.__class__.__name__)
        return self._update_preset_from_mod_config()


class OpenVrFsrMod(OpenVrMod):
    def __init__(self, options: Iterator[BaseOptions], location: Path):
        super(OpenVrFsrMod, self).__init__(options, location, FsrMod)


class OpenVrFoveatedMod(OpenVrMod):
    def __init__(self, options: Iterator[BaseOptions], location: Path):
        super(OpenVrFoveatedMod, self).__init__(options, location, FoveatedMod)
