import logging
from pathlib import Path
from typing import Iterator
from zipfile import ZipFile

from rf2settings.globals import get_data_dir, RESHADE_ZIP, RESHADE_PRESET_DIR, RESHADE_TARGET_PRESET_NAME
from rf2settings.preset.settings_model import BaseOptions


class VrToolKit:
    dll_tgt = ('ReShade64.dll', 'dxgi.dll')
    preprocessor_name = 'PreprocessorDefinitions'
    preprocessor = {'VRT_SHARPENING_MODE': 0, 'VRT_USE_CENTER_MASK': 0, 'VRT_DITHERING': 0,
                    'VRT_COLOR_CORRECTION_MODE': 0, 'VRT_ANTIALIASING_MODE': 0}
    ini_settings = {'iCircularMaskSize': None, 'iCircularMaskSmoothness': None, 'iCircularMaskHorizontalOffset': None,
                    'iDitheringStrength': None,
                    'Strength': None, 'Offset': None, 'Clamp': None,
                    'Contrast': None, 'Sharpening': None,
                    'Gamma': None, 'Exposure': None, 'Saturation': None,
                    'Subpix': None, 'EdgeThreshold': None, 'EdgeThresholdMin': None, }

    def __init__(self, options: Iterator[BaseOptions], location: Path):
        self.options = options
        self.location = location

        self.error = str()

    def _update_options(self) -> bool:
        use_reshade = False

        # -- Read Preset options
        for preset_options in self.options:
            for option in preset_options.options:
                if option.key == 'use_reshade':
                    use_reshade = option.value
                elif option.key in self.preprocessor:
                    self.preprocessor[option.key] = option.value
                elif option.key in self.ini_settings:
                    self.ini_settings[option.key] = option.value

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
                        reshade_removed = True

                    # - Remove files matching zip file
                    if file.is_file():
                        logging.info('Removing ReShade file %s from rF2 bin dir.', file)
                        file.unlink(missing_ok=True)
                        reshade_removed = True
                    else:
                        if file.exists():
                            remove_dirs.append(file)

        return remove_dirs

    def _update_preset_ini(self, reshade_preset: Path):
        preprocessor_values = ''
        for k, v in self.preprocessor.items():
            preprocessor_values += f'{"," if preprocessor_values else ""}{k}={v}'

        # -- Update Preset Ini file
        try:
            # - Read Preset Ini file
            with open(reshade_preset, 'r') as f:
                preset_lines = f.readlines()

            # -- Apply settings to Preset Ini file lines
            configured_preset_lines = list()
            for line in preset_lines:
                if line.startswith(self.preprocessor_name) and preprocessor_values:
                    line = f'{self.preprocessor_name}={preprocessor_values}\n'
                for k, v in self.ini_settings.items():
                    if line.startswith(k):
                        line = f'{k}={v:.6f}\n'
                configured_preset_lines.append(line)

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
