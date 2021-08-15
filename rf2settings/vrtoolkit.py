import logging
import shutil
from pathlib import Path
from typing import Iterator
from zipfile import ZipFile

from rf2settings.globals import get_data_dir, RESHADE_ZIP, RESHADE_PRESET_DIR, RESHADE_TARGET_PRESET_NAME
from rf2settings.preset.settings_model import BaseOptions
from rf2settings.settingsdef import graphics


class VrToolKit:
    dll_tgt = ('ReShade64.dll', 'dxgi.dll')
    extra_files = [
        ('rF2_nonPBRmodDay1.png', 'ReShade/Textures'),
        ('rF2_nonPBRmodDay2.png', 'ReShade/Textures'),
        ('lut_ams.png', 'ReShade/Textures'),
        ('lut_gtr2.png', 'ReShade/Textures'),
        ('lut_rbr.png', 'ReShade/Textures'),
        ('lut_filmic_basic.png', 'ReShade/Textures'),
        ('lut_provia.png', 'ReShade/Textures'),
        ('lut_technicolor.png', 'ReShade/Textures'),
    ]
    preprocessor_name = 'PreprocessorDefinitions'
    preprocessor = {'VRT_SHARPENING_MODE': 0, 'VRT_USE_CENTER_MASK': 0, 'VRT_DITHERING': 0,
                    'VRT_COLOR_CORRECTION_MODE': 0, 'VRT_ANTIALIASING_MODE': 0, 'fLUT_TextureName': '"lut.png"'}

    def __init__(self, options: Iterator[BaseOptions], location: Path):
        self.options = options
        self.location = location

        self.error = str()
        self.ini_settings = dict()
        self.ini_default_settings = dict()
        self._read_setting_defaults()

    def _read_setting_defaults(self):
        settings_dict = dict()
        settings_dict.update(graphics.reshade_fas)
        settings_dict.update(graphics.reshade_dither)
        settings_dict.update(graphics.reshade_mask)
        settings_dict.update(graphics.reshade_aa)
        settings_dict.update(graphics.reshade_cas)
        settings_dict.update(graphics.reshade_cc)
        settings_dict.update(graphics.reshade_lut)

        for key, setting in settings_dict.items():
            self.ini_settings[key] = setting.get('value')
            self.ini_default_settings[key] = setting.get('value')

    def _update_options(self, update_from_disk: bool = False) -> bool:
        use_reshade = False

        # -- Iterate Preset options
        for preset_options in self.options:
            for option in preset_options.options:
                # -- Read from Preset options
                if not update_from_disk:
                    if option.key == 'use_reshade':
                        use_reshade = option.value
                    elif option.key in self.preprocessor:
                        self.preprocessor[option.key] = option.value
                    elif option.key in self.ini_settings:
                        self.ini_settings[option.key] = option.value
                # -- Write to Preset options
                else:
                    if option.key == 'use_reshade':
                        option.value = True
                        option.exists_in_rf = True
                    elif option.key in self.preprocessor:
                        option.value = self.preprocessor[option.key]
                        option.exists_in_rf = True
                    elif option.key in self.ini_settings:
                        option.value = self.ini_settings[option.key]
                        option.exists_in_rf = True

        return use_reshade

    def _work_thru_reshade_release_zip(self, use_reshade: bool, bin_dir: Path) -> list:
        reshade_zip = get_data_dir() / RESHADE_ZIP
        remove_dirs = list()

        with ZipFile(reshade_zip, 'r') as zip_obj:
            for zip_info in zip_obj.filelist:
                file = bin_dir / zip_info.filename

                # -- Extract Zip member
                if use_reshade:
                    # -- Skip existing files
                    if file.exists():
                        continue

                    logging.info('Extracting ReShade file %s to rF2 bin dir.', file)
                    zip_obj.extract(zip_info, path=bin_dir)

                    # - ReShade64.dll -> dxgi.dll
                    if self.dll_tgt[0] == zip_info.filename:
                        new_file = bin_dir / self.dll_tgt[1]
                        new_file.unlink(missing_ok=True)
                        try:
                            file.rename(new_file)
                        except Exception as e:
                            logging.error('Could not rename file: %s', e)
                # -- Remove files found in zip
                else:
                    # - Remove renamed dll
                    dll_file = Path(file.parent / self.dll_tgt[1])
                    if dll_file.is_file():
                        dll_file.unlink(missing_ok=True)
                        logging.info('Removing ReShade file %s from rF2 bin dir.', dll_file)

                    # - Remove files matching zip file
                    if file.is_file():
                        logging.info('Removing ReShade file %s from rF2 bin dir.', file)
                        file.unlink(missing_ok=True)
                    else:
                        if file.exists():
                            remove_dirs.append(file)

        # -- Copy/Remove extra files
        for (file_name, file_target_dir) in self.extra_files:
            src_file = get_data_dir() / file_name
            target_file = bin_dir / file_target_dir / file_name

            try:
                # -- Copy file
                if use_reshade:
                    shutil.copyfile(src_file, target_file)
                # -- Remove file
                else:
                    target_file.unlink(missing_ok=True)
            except Exception as e:
                logging.error('Could not process extra file %s: %s', file_name, e)

        return remove_dirs

    @staticmethod
    def _add_ini_value_line(key, value):
        if isinstance(value, (str, int)):
            return f'{key}={value}\n'
        else:
            return f'{key}={value:.6f}\n'

    def _update_preset_ini(self, reshade_preset: Path):
        """ Write updated values to Generic VRToolKit Preset """
        p_dict, preprocessor_values = self.preprocessor.copy(), ''
        # -- Remove fLUT_TextureName if Color Correction Mode != LUT
        if p_dict['VRT_COLOR_CORRECTION_MODE'] != 1:
            p_dict.pop('fLUT_TextureName')

        # -- Prepare Preprocessor values
        for k, v in p_dict.items():
            preprocessor_values += f'{"," if preprocessor_values else ""}{k}={v}'

        # -- Update Preset Ini file
        try:
            # -- Read Preset Ini file
            with open(reshade_preset, 'r') as f:
                preset_lines = f.readlines()

            # -- Apply settings to Preset Ini file lines
            configured_preset_lines = list()
            for line in preset_lines:
                if line.startswith(self.preprocessor_name) and preprocessor_values:
                    line = f'{self.preprocessor_name}={preprocessor_values}\n'
                configured_preset_lines.append(line)

                if line.replace('\r', '').replace('\n', '') == '[VRToolkit.fx]':
                    break

            # -- Add Ini Settings
            for k, v in self.ini_settings.items():
                if v == self.ini_default_settings[k]:
                    continue
                configured_preset_lines.append(self._add_ini_value_line(k, v))

            # - Write Preset Ini file
            logging.info('Updating ReShade Preset file: %s', reshade_preset)
            with open(reshade_preset, 'w') as f:
                f.writelines(configured_preset_lines)

            for line in configured_preset_lines:
                logging.debug('Updated VRToolkit Setting: %s', line.replace('\r', '').replace('\n', ''))
        except Exception as e:
            msg = f'Error writing Reshade Preset Ini file: {e}'
            logging.error(msg)
            self.error = msg
            return False
        return True

    def write(self):
        use_reshade = self._update_options()

        bin_dir = self.location / 'Bin64'
        reshade_preset = bin_dir / RESHADE_PRESET_DIR / RESHADE_TARGET_PRESET_NAME
        reshade_removed = False

        # -- Extract ReShade files
        logging.info('Applying ReShade settings: %s', use_reshade)
        remove_dirs = self._work_thru_reshade_release_zip(use_reshade, bin_dir)

        # -- Remove ReShade directories and files
        if not use_reshade:
            # -- Remove Cache
            cache = bin_dir / 'ReShade' / 'Cache'
            for f in cache.glob('*.*'):
                f.unlink()

            # -- Remove ReShade preset
            if reshade_preset.exists():
                reshade_preset.unlink()

            # -- Remove empty ReShade dirs
            if remove_dirs:
                for d in sorted(remove_dirs, key=lambda x: len(x.as_posix()), reverse=True):
                    try:
                        d.rmdir()
                    except Exception as e:
                        # Eg. if the use has saved screenshots, directory will not be removed
                        msg = f'Will not delete ReShade directory with user data: {e}'
                        logging.error(msg)
                        self.error += msg

            return reshade_removed

        # -- Prepare writing of ReShade Preset file
        return self._update_preset_ini(reshade_preset)

    def _read_preset_ini(self, reshade_preset: Path) -> bool:
        """ Lookup current VRToolkit Settings on disk """
        if not reshade_preset.exists():
            return False

        try:
            # - Read Preset Ini file
            with open(reshade_preset, 'r') as f:
                preset_lines = f.readlines()

            # - Read settings from Preset Ini file lines
            for line in preset_lines:
                if line.startswith(self.preprocessor_name):
                    p_str = line.replace(f'{self.preprocessor_name}=', '').replace('\n', '')
                    for p_def in p_str.split(','):
                        key, value = p_def.split('=', 2)
                        if key in self.preprocessor:
                            if value.isnumeric():
                                self.preprocessor[key] = int(value)
                            else:
                                self.preprocessor[key] = value
                for k, v in self.ini_settings.items():
                    if line.startswith(k):
                        value = line.replace(f'{k}=', '').replace('\n', '')
                        if isinstance(value, str) and value.split('.')[0].isnumeric():
                            # -- Read int
                            if value.isdigit():
                                self.ini_settings[k] = int(value)
                            # -- Read float
                            else:
                                self.ini_settings[k] = float(value)
                        else:
                            # -- Read str
                            self.ini_settings[k] = value

            # -- Update RfactorPlayer VRToolkit Settings
            self._update_options(update_from_disk=True)
        except Exception as e:
            msg = f'Error reading Reshade Preset Ini file: {e}'
            logging.error(msg)
            self.error = msg
            return False
        return True

    def read(self) -> bool:
        bin_dir = self.location / 'Bin64'
        reshade_preset = bin_dir / RESHADE_PRESET_DIR / RESHADE_TARGET_PRESET_NAME

        return self._read_preset_ini(reshade_preset)
