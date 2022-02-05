import logging
from typing import Union, List, Optional

from open_vr_mod.cfg import FsrSettings, FoveatedSettings
from ..settingsdef import graphics, generic, controls, headlights
from ..utils import JsonRepr

_allowed_value_types = (bool, str, int, float)


class OptionsTarget:
    player_json = 0
    controller_json = 1
    dx_config = 10
    reshade = 20
    webui_session = 30
    webui_content = 40
    open_vr_fsr = 50
    open_vr_fov = 51
    app_settings = 100


class Option(JsonRepr):
    # No need to save these internal attributes
    skip_keys = ['dupl']
    # Entries we don't want to export or save
    export_skip_keys = ['settings', 'hidden', 'ini_type', 'desc', 'name', 'exists_in_rf',
                        'difference', 'difference_value', 'dupl']

    def __init__(self):
        self.key = 'Player JSON key'
        self.name = 'Friendly Setting Name'

        # Current value
        self.value: Union[_allowed_value_types] = None

        # Extra Attributes
        self.hidden: bool = False
        self.ini_type = None
        self.exists_in_rf = False  # Mark options not found on disk so we can ignore them during comparison and saving
        self.difference = False
        self.difference_value = None
        self.dupl = None  # Mark options that need another value written eg. GPRIX Time + CURNT Time

        # Possible settings
        self.settings: tuple = tuple()

    def __eq__(self, other):
        """ Report difference between options

        :param modules.settings_model.Option other:
        :return: True if self.value if differs
        """
        # -- Ignore null values and hidden settings
        if self.value is None or other.value is None or self.hidden:
            return True

        if other.value != self.value or other.key != self.key:
            logging.debug('Option %s %s differs from current setting %s %s',
                          other.key, other.value, self.key, self.value)

            # -- Report difference to FrontEnd
            self.difference = True
            self.difference_value = other.value
            return False
        return True


class BaseOptions(JsonRepr):
    # Read only options we want to read but never write to rF/save or export eg. Driver Name
    skip_keys = ['title', 'ignore_equal', 'mandatory', 'key']
    # Key representing the category key in player_json
    key = 'Base Options'
    # Key representing the field name for Preset and RfactorPlayer classes
    # must be unique per class!
    app_key = 'base_options'
    # Category Title to be displayed in front end
    title = 'Base Settings'
    # Target to indicate RfactorPlayer where to write these options
    # eg. OptionsTarget.player_json
    target = None
    # Set rfactor instance to invalid and block the app with an error
    # if none of these options could be found
    mandatory = True
    # Ignore comparison with disk settings
    ignore_equal = False

    def __init__(self, options: List[Option] = None):
        if options is None:
            options = []
        self.options: List[Option] = options

    def read_from_python_dict(self, options_dict: dict):
        self.options = list()

        for key, detail_dict in options_dict.items():
            option = Option()
            option.key = key
            option.name = detail_dict.get('name', 'Unknown')
            option.settings = tuple(detail_dict.get('settings', list()))
            option.value = detail_dict.get('value')
            option.desc = detail_dict.get('desc')
            option.hidden = detail_dict.get('hidden')
            option.ini_type = detail_dict.get('_type')
            option.dupl = detail_dict.get('_dupl')
            self.options.append(option)

    def to_js(self, export: bool = False) -> dict:
        return {'key': self.key, 'title': self.title,
                'options': [option.to_js_object(export) for option in self.options]}

    def to_webui_js(self) -> dict:
        webui_dict = dict()
        for option in self.options:
            webui_dict[option.key] = option.value

        return webui_dict

    def get_option(self, key) -> Optional[Option]:
        o = [o for o in self.options if o.key == key]
        if o:
            return o[0]

    def from_js_dict(self, json_dict):
        for k, v in json_dict.items():
            if k == 'options':
                # -- Read only values for Option objects that already exist
                #    We assume the BaseOptions object has been initialized in it's
                #    sub-classes with valid default settings.
                for js_opt in v:
                    _k, _v = js_opt.get('key'), js_opt.get('value')
                    opt = self.get_option(_k)
                    if opt and _v is not None:
                        opt.value = _v
            else:
                if k in self.skip_keys:
                    continue
                setattr(self, k, v)

    def __eq__(self, other):
        """ Report difference between options

        :param modules.settings_model.BaseOptions other:
        :return: True if other options differ
        """
        if self.ignore_equal:
            return True

        if other.key != self.key:
            logging.info('Options key difference: %s != %s', other.key, self.key)
            return False

        # -- Compare every Option
        #    sort both .options by their keys
        options = sorted(self.options, key=lambda k: k.key)
        other_options = sorted(other.options, key=lambda k: k.key)

        # - FrontEnd variant
        #   Slower but will mark all settings differences for FrontEnd display
        equals = True
        for a, b in zip(options, other_options):
            if a.key not in self.skip_keys and a.exists_in_rf:
                if a != b:
                    equals = False

        # - Performance variant
        #   Quicker as it exits as soon as it finds the first difference
        # return all((a == b for a, b in zip(options, other_options) if a.key not in self.skip_keys and a.exists_in_rf))

        return equals


class DriverOptions(BaseOptions):
    skip_keys = ['Player Name', 'Player Nick']
    key = 'DRIVER'
    app_key = 'driver_options'
    title = 'Driver Settings'
    target = OptionsTarget.player_json

    def __init__(self):
        super(DriverOptions, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(generic.driver_settings)


class GameOptions(BaseOptions):
    key = 'Game Options'
    app_key = 'game_options'
    title = 'Game Settings'
    target = OptionsTarget.player_json

    def __init__(self):
        super(GameOptions, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(generic.game_settings)


class MiscOptions(BaseOptions):
    key = 'Miscellaneous'
    app_key = 'misc_options'
    title = 'Miscellaneous'
    target = OptionsTarget.player_json

    def __init__(self):
        super(MiscOptions, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(generic.misc_settings)


class AppControllerAssignments(BaseOptions):
    key = 'App_Controller_Assignments'
    app_key = 'app_controller_assignments'
    title = 'App Controller Assignments'
    defaults = generic.app_controller_assignments
    target = OptionsTarget.app_settings

    def __init__(self):
        super(AppControllerAssignments, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(generic.app_controller_assignments)


class GamepadMouseOptions(BaseOptions):
    key = 'Controls'
    app_key = 'gamepad_mouse_settings'
    title = 'UI Gamepad Mouse Settings'
    target = OptionsTarget.player_json

    def __init__(self):
        super(GamepadMouseOptions, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(controls.ui_gamepad_mouse_settings)


class FreelookOptions(BaseOptions):
    key = 'General Controls'
    app_key = 'freelook_settings'
    title = 'Freelook Settings'
    target = OptionsTarget.controller_json
    mandatory = False

    def __init__(self):
        super(FreelookOptions, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(controls.freelook_controls)


class GeneralSteeringOptions(BaseOptions):
    key = 'General Controls'
    app_key = 'general_steering_settings'
    title = 'Steering Wheel Settings'
    target = OptionsTarget.controller_json
    mandatory = False

    def __init__(self):
        super(GeneralSteeringOptions, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(controls.general_steering)


class GraphicOptions(BaseOptions):
    key = 'Graphic Options'
    app_key = 'graphic_options'
    title = 'Display Settings'
    target = OptionsTarget.player_json

    def __init__(self):
        super(GraphicOptions, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(graphics.adjustable_graphics_settings)


class GraphicViewOptions(BaseOptions):
    key = 'Graphic Options'
    app_key = 'graphic_view_options'
    title = 'View Settings'
    target = OptionsTarget.player_json

    def __init__(self):
        super(GraphicViewOptions, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(graphics.view_settings)


class VideoSettings(BaseOptions):
    key = 'Video Settings'
    app_key = 'video_settings'
    title = 'Video Settings'
    target = OptionsTarget.dx_config

    def __init__(self):
        super(VideoSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(graphics.adjustable_video_settings)


class ReshadeSettings(BaseOptions):
    key = 'reshade_settings'
    app_key = 'reshade_settings'
    title = 'VRToolkit'
    target = OptionsTarget.reshade
    mandatory = False

    def __init__(self):
        super(ReshadeSettings, self).__init__()

        # -- Read Default options
        settings_dict = dict()
        settings_dict.update(graphics.reshade_settings)
        settings_dict.update(graphics.reshade_dither)
        settings_dict.update(graphics.reshade_mask)
        self.read_from_python_dict(settings_dict)


class ReshadeFasSettings(BaseOptions):
    key = 'reshade_fas_settings'
    app_key = 'reshade_fas_settings'
    title = 'Filmic Anamorph Sharpen'
    target = OptionsTarget.reshade
    mandatory = False

    def __init__(self):
        super(ReshadeFasSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(graphics.reshade_fas)


class ReshadeCasSettings(BaseOptions):
    key = 'reshade_cas_settings'
    app_key = 'reshade_cas_settings'
    title = 'AMD Fidelity FX (CAS)'
    target = OptionsTarget.reshade
    mandatory = False

    def __init__(self):
        super(ReshadeCasSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(graphics.reshade_cas)


class ReshadeLutSettings(BaseOptions):
    key = 'reshade_lut_settings'
    app_key = 'reshade_lut_settings'
    title = 'Look Up Table'
    target = OptionsTarget.reshade
    mandatory = False

    def __init__(self):
        super(ReshadeLutSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(graphics.reshade_lut)


class ReshadeCcSettings(BaseOptions):
    key = 'reshade_cc_settings'
    app_key = 'reshade_cc_settings'
    title = 'Basic Color Correction'
    target = OptionsTarget.reshade
    mandatory = False

    def __init__(self):
        super(ReshadeCcSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(graphics.reshade_cc)


class ReshadeAaSettings(BaseOptions):
    key = 'reshade_aa_settings'
    app_key = 'reshade_aa_settings'
    title = 'FXAA'
    target = OptionsTarget.reshade
    mandatory = False

    def __init__(self):
        super(ReshadeAaSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(graphics.reshade_aa)


class OpenVrFsrSettings(BaseOptions):
    key = 'openvrfsr_settings'
    app_key = 'openvrfsr_settings'
    title = 'OpenVR FSR'
    target = OptionsTarget.open_vr_fsr
    mandatory = False

    def __init__(self):
        super(OpenVrFsrSettings, self).__init__()

        # -- Read Default options
        fsr_cfg = FsrSettings()

        # -- Tweak defaults
        fsr_cfg.enabled.value = False
        fsr_cfg.sharpness.value = 0.0
        fsr_cfg.sharpness.settings[0]['min'] = 0.0
        fsr_cfg.applyMIPBias.value = False
        self.read_from_python_dict(fsr_cfg.to_dict(category_filter=['FSR Settings']))


class OpenVrFsrHotKeySettings(BaseOptions):
    key = 'openvrfsr_hk_settings'
    app_key = 'openvrfsr_hk_settings'
    title = 'OpenVR FSR HotKeys'
    target = OptionsTarget.open_vr_fsr
    mandatory = False

    def __init__(self):
        super(OpenVrFsrHotKeySettings, self).__init__()

        # -- Read Default options
        fsr_cfg = FsrSettings()
        self.read_from_python_dict(fsr_cfg.to_dict(category_filter=['Hotkey Settings', 'Hotkeys']))


class OpenVrFoveatedSettings(BaseOptions):
    key = 'openvrfoveated_settings'
    app_key = 'openvrfoveated_settings'
    title = 'OpenVR Foveated'
    target = OptionsTarget.open_vr_fov
    mandatory = False

    def __init__(self):
        super(OpenVrFoveatedSettings, self).__init__()

        # -- Read Default options
        fov_cfg = FoveatedSettings()

        # -- Tweak defaults
        fov_cfg.enabled.value = False
        fov_cfg.sharpenEnabled.value = False
        self.read_from_python_dict(fov_cfg.to_dict(
            category_filter=['FFR Settings', 'FFR Radius', 'Sharpness Settings'])
        )


class OpenVrFoveatedHotkeySettings(BaseOptions):
    key = 'openvrfoveated_hk_settings'
    app_key = 'openvrfoveated_hk_settings'
    title = 'OpenVR Foveated HotKeys'
    target = OptionsTarget.open_vr_fov
    mandatory = False

    def __init__(self):
        super(OpenVrFoveatedHotkeySettings, self).__init__()

        # -- Read Default options
        fov_cfg = FoveatedSettings()
        self.read_from_python_dict(fov_cfg.to_dict(category_filter=['Hotkey Settings', 'Hotkeys']))


class ResolutionSettings(BaseOptions):
    key = 'Resolution Settings'
    app_key = 'resolution_settings'
    title = 'Resolution and Window Settings'
    target = OptionsTarget.dx_config

    def __init__(self):
        super(ResolutionSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(graphics.resolution_video_settings)


class AdvancedGraphicSettings(BaseOptions):
    key = 'Graphic Options'
    app_key = 'advanced_graphic_options'
    title = 'Advanced Display Settings'
    target = OptionsTarget.player_json

    def __init__(self):
        super(AdvancedGraphicSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(graphics.advanced_settings)


class AutoHeadlightSettings(BaseOptions):
    """ rFactors build-in Auto-Headlight from >= v1124RC """
    key = 'DRIVING AIDS'
    app_key = 'auto_headlight_settings'
    title = 'Auto Headlight rFactor Aid'
    target = OptionsTarget.player_json
    mandatory = False

    def __init__(self):
        super(AutoHeadlightSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(headlights.auto_headlight_rfactor)


class HeadlightSettings(BaseOptions):
    key = 'headlight_settings'
    app_key = 'headlight_settings'
    title = 'Headlight Settings'
    target = OptionsTarget.app_settings

    def __init__(self):
        super(HeadlightSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(headlights.headlight_settings)


class HeadlightControllerJsonSettings(BaseOptions):
    key = 'Input'
    app_key = 'headlight_controller_json'
    title = 'Headlight rFactor Control Mapping'
    target = OptionsTarget.controller_json
    mandatory = False

    def __init__(self):
        super(HeadlightControllerJsonSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(headlights.headlight_rfactor)


class BenchmarkSettings(BaseOptions):
    key = 'benchmark_settings'
    app_key = 'benchmark_settings'
    title = 'Benchmark Settings'
    target = OptionsTarget.app_settings

    def __init__(self):
        super(BenchmarkSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(generic.benchmark_settings)


class BenchmarkControllerJsonSettings(BaseOptions):
    """ Helper object to locate AI Control and Show FPS keycodes """
    key = 'Input'
    app_key = 'benchmark_controller_json'
    title = 'Benchmark rFactor Control Mapping'
    target = OptionsTarget.controller_json
    mandatory = False

    def __init__(self):
        super(BenchmarkControllerJsonSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(controls.benchmark_rfactor)


class SessionUiSettings(BaseOptions):
    key = 'Session UI Options'
    app_key = 'session_ui_settings'
    title = 'Session Ui Settings'
    target = OptionsTarget.webui_session
    ignore_equal = True

    def __init__(self):
        super(SessionUiSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(generic.session_ui_settings)


class ContentUiSettings(BaseOptions):
    key = 'Content UI Options'
    app_key = 'content_ui_settings'
    title = 'Content Selection'
    target = OptionsTarget.webui_content

    def __init__(self):
        super(ContentUiSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(generic.content_ui_settings)


class SessionGameSettings(BaseOptions):
    key = 'Game Options'
    app_key = 'session_game_settings'
    title = 'Session Settings'
    target = OptionsTarget.player_json

    def __init__(self):
        super(SessionGameSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(generic.session_settings)


class SessionConditionSettings(BaseOptions):
    key = 'Race Conditions'
    app_key = 'session_condition_settings'
    title = 'Race Conditions'
    target = OptionsTarget.player_json

    def __init__(self):
        super(SessionConditionSettings, self).__init__()

        # -- Read Default options
        self.read_from_python_dict(generic.session_conditions)


# ------------------------------------------------
# Direct json Options not wrapped in BaseOptions #
# ------------------------------------------------
class HeadlightControllerAssignments(JsonRepr):
    app_key = 'headlight_controller_assignments'
    title = 'Headlight Controller Assignments'
    defaults = headlights.controller_assignments

    def __init__(self):
        super(HeadlightControllerAssignments, self).__init__()
        self.after_load_callback = self.set_missing_defaults
        self.options = headlights.controller_assignments
