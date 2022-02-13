import json
import logging
from pathlib import Path
from typing import Iterable, Tuple, Optional

from . import settings_model
from .presets_dir import get_user_presets_dir, get_user_export_dir
from .settings_model_base import OPTION_CLASSES
from ..utils import create_file_safe_name


class PresetType:
    graphics = 0
    advanced_settings = 1
    controls = 2
    session = 3


class BasePreset:
    # Defines which type of options this Preset represents
    preset_type: int = -1
    option_class_keys = set()
    prefix = ''

    def __init__(self, name: str = None, desc: str = None):
        """ Preset Base Type representing a set <option_class_keys> of BaseOptions
            Presets handle the loading and saving of the settings provided in BaseOptions to a JSON file.
        """
        self.name = name or 'Default'
        self.desc = desc or 'The [Current Settings] preset represents the settings ' \
                            'currently found in your rFactor 2 installation.'

        # -- Set BaseOptions as Preset fields
        #    eg. Preset.video_settings: VideoSettings
        for key in self.option_class_keys:
            options_instance = OPTION_CLASSES.get(key)()
            setattr(self, key, options_instance)

    def update(self, rf, preset_name: str = 'Current Settings'):
        """ Update current preset from the actual rFactor 2 settings on disk

        :param preset_name: Create a preset name [preset_name] [PlayerJson Nickname]
        :param modules.rfactor.RfactorPlayer rf:
        :return:
        """
        # Update Graphic Options, Video Settings etc. from rF object
        for key, options in self.iterate_options():
            if options.target == settings_model.OptionsTarget.webui_session:
                # Skip options not readable from disk
                continue
            setattr(self, key, getattr(rf.options, key))

        # Set Preset Name from Player Nick
        try:
            for o in getattr(rf.options, 'driver_options').options:
                if o.key == 'Player Nick':
                    self.name = f'{preset_name} [{o.value}]'
        except Exception as e:
            logging.error('Could not locate driver name: %s', e)
            self.name = f'Current Settings [NA]'

    def find_unique_preset_name(self) -> str:
        base_name = create_file_safe_name(self.name)
        name = base_name
        name_idx = 0
        preset_dir = get_user_presets_dir()

        while [_ for _ in preset_dir.glob(f'*{name}*.json')]:
            name_idx += 1
            name = f'{base_name}_{name_idx}'

        return name

    def save_unique_file(self) -> bool:
        return self.export(self.find_unique_preset_name())

    def additional_save_operations(self):
        """ Should be overwritten in sub classes """
        pass

    def additional_export_operations(self):
        """ Should be overwritten in sub classes """
        pass

    def export(self, unique_name: str = None, export_dir: Optional[Path] = None,
               keep_export_data: bool = False) -> bool:
        file_name = create_file_safe_name(unique_name or self.name)
        if export_dir is None:
            file = get_user_export_dir() / f'{file_name}.json'
        else:
            file = export_dir / f'{file_name}.json'
        self.name = unique_name or self.name

        # -- Weather to export unsafe data like e.g. video mode
        #    Default is False
        if not keep_export_data:
            self.additional_export_operations()

        return self._save_to_file(file)

    def save(self) -> bool:
        file_name = create_file_safe_name(f'{self.prefix}_{self.name}')
        file = get_user_presets_dir() / f'{file_name}.json'
        self.additional_save_operations()

        return self._save_to_file(file)

    def _save_to_file(self, file) -> bool:
        try:
            with open(file.as_posix(), 'w') as f:
                json.dump(self.to_js(export=True), f, indent=2, sort_keys=True)
        except Exception as e:
            logging.fatal('Could not write Preset export! %s', e)
            return False
        return True

    def iterate_options(self) -> Iterable[Tuple[str, settings_model.BaseOptions]]:
        """ Helper to iterate thru all BaseOptions assigned to the preset. """
        for key in self.option_class_keys:
            yield key, getattr(self, key)

    def to_js(self, export: bool = False):
        """ Convert to json serializable dictionary """
        preset_dict = {k: v.to_js(export) for k, v in self.iterate_options()}
        preset_dict['name'] = self.name
        preset_dict['desc'] = self.desc
        preset_dict['preset_type'] = self.preset_type
        return preset_dict

    def from_js_dict(self, js_dict):
        """ Update Preset object from a json dictionary """
        self.name = js_dict.get('name')
        self.desc = js_dict.get('desc')

        for key, _ in self.iterate_options():
            options_class = OPTION_CLASSES.get(key)
            options_instance = options_class()
            options_instance.from_js_dict(js_dict.get(key, dict()))
            setattr(self, key, options_instance)

    def __eq__(self, other):
        """ Report difference between presets

        :param modules.preset.Preset other:
        :return: True if other options differ
        """
        equals = True
        for key, options in self.iterate_options():
            if getattr(other, key) != options:
                logging.debug('Compared Presets %s to %s. Found deviating options in %s',
                              self.name, other.name, options.title)
                equals = False
        return equals


class GraphicsPreset(BasePreset):
    preset_type: int = PresetType.graphics
    option_class_keys = {settings_model.GraphicOptions.app_key, settings_model.GraphicViewOptions.app_key,
                         settings_model.AdvancedGraphicSettings.app_key,
                         settings_model.VideoSettings.app_key, settings_model.ResolutionSettings.app_key,
                         settings_model.ReshadeSettings.app_key, settings_model.ReshadeFasSettings.app_key,
                         settings_model.ReshadeCasSettings.app_key, settings_model.ReshadeAaSettings.app_key,
                         settings_model.ReshadeLutSettings.app_key, settings_model.ReshadeCcSettings.app_key,
                         settings_model.ReshadeClaritySettings.app_key,
                         settings_model.OpenVrFsrSettings.app_key, settings_model.OpenVrFsrHotKeySettings.app_key,
                         settings_model.OpenVrFoveatedSettings.app_key,
                         settings_model.OpenVrFoveatedHotkeySettings.app_key,
                         }
    prefix = 'gfx'

    def __init__(self, name: str = None, desc: str = None):
        """ Presets for graphical preferences """
        super(GraphicsPreset, self).__init__(name, desc)

    def additional_export_operations(self):
        # Reset Resolution Settings
        default_res_settings = settings_model.ResolutionSettings()
        setattr(self, settings_model.ResolutionSettings.app_key, default_res_settings)


class AdvancedSettingsPreset(BasePreset):
    preset_type: int = PresetType.advanced_settings
    option_class_keys = {settings_model.DriverOptions.app_key, settings_model.GameOptions.app_key,
                         settings_model.MiscOptions.app_key}
    prefix = 'adv_settings'

    def __init__(self, name: str = None, desc: str = None):
        super(AdvancedSettingsPreset, self).__init__(name, desc)

    def additional_export_operations(self):
        pass

    def additional_save_operations(self):
        pass


class ControlsSettingsPreset(BasePreset):
    preset_type: int = PresetType.controls
    option_class_keys = {settings_model.GamepadMouseOptions.app_key, settings_model.FreelookOptions.app_key,
                         settings_model.GeneralSteeringOptions.app_key}
    prefix = 'controls'

    def __init__(self, name: str = None, desc: str = None):
        super(ControlsSettingsPreset, self).__init__(name, desc)


class SessionPreset(BasePreset):
    preset_type: int = PresetType.session
    option_class_keys = {settings_model.SessionGameSettings.app_key,
                         settings_model.SessionConditionSettings.app_key,
                         settings_model.SessionUiSettings.app_key,
                         settings_model.ContentUiSettings.app_key}
    prefix = 'race_session'

    def __init__(self, name: str = None, desc: str = None):
        super(SessionPreset, self).__init__(name, desc)


class HeadlightControlsSettingsPreset(BasePreset):
    option_class_keys = {settings_model.HeadlightControllerJsonSettings.app_key,
                         settings_model.AutoHeadlightSettings.app_key}
    prefix = 'hdl_controls'

    def __init__(self, name: str = None, desc: str = None):
        super(HeadlightControlsSettingsPreset, self).__init__(name, desc)
