import enum
import logging
import math
import os
import os.path
import re
import subprocess as sp
import time
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Tuple, Union, Optional, Dict, Any
import ctypes

import eel
import gevent
import psutil

from .globals import get_settings_dir, FROZEN

try:
    import winreg as registry

    WINREG_AVAIL = True
except ImportError:
    registry = None
    WINREG_AVAIL = False

try:
    import pygame
    pygame_avail = 1
except ImportError:
    pygame_avail = 0


def create_file_safe_name(filename: str, allow_spaces: bool = False) -> str:
    """ Replace any non alphanumeric characters from a string expect minus/underscore/period """
    if not allow_spaces:
        return re.sub('[^\\w\\-_.]', '_', filename)
    return re.sub('[^\\w\\- _.]', '_', filename)


class JsonRepr:
    skip_keys = list()
    export_skip_keys = list()
    after_load_callback: Optional[callable] = None
    before_save_callback: Optional[callable] = None

    @staticmethod
    def update_skip_keys(keys):
        return set(keys).union({'skip_keys', 'export_skip_keys'})

    def to_js_object(self, export: bool = False) -> dict:
        if self.before_save_callback:
            self.before_save_callback()

        self.skip_keys = self.update_skip_keys(self.skip_keys)

        js_dict = dict()
        for k, v in self.__dict__.items():
            if (export and k in self.export_skip_keys) or k in self.skip_keys:
                continue
            if k[:2] == '__' or callable(v) or isinstance(v, (classmethod, staticmethod)):
                continue

            js_dict[k] = v
        return js_dict

    def from_js_dict(self, json_dict):
        self.skip_keys = self.update_skip_keys(self.skip_keys)

        for k, v in json_dict.items():
            if k in self.skip_keys:
                continue
            setattr(self, k, v)

        if self.after_load_callback:
            self.after_load_callback()

    def set_missing_defaults(self):
        """ Set this as after load callback to make sure all defined
            default options are there.
        """
        if hasattr(self, 'defaults') and hasattr(self, 'options'):
            # -- Set defaults that were not loaded
            for k, opt in self.defaults.items():
                if k not in self.options:
                    self.options[k] = opt

            # -- Remove options no longer available
            for k, opt in self.options.items():
                if k not in self.defaults:
                    self.options.pop(k)


class AppExceptionHook:
    app = None
    event = gevent.event.Event()
    gui_msg = ''
    produce_exception = False

    @classmethod
    def exception_hook(cls, etype, value, tb):
        """ sys.excepthook will call this method """
        import traceback

        # Print exception
        traceback.print_exception(etype, value, tb)

        # Log exception
        stacktrace_msg = ''.join(traceback.format_tb(tb))
        if etype:
            exception_msg = '{0}: {1}'.format(etype, value)
        else:
            exception_msg = 'Exception: {}'.format(value)

        logging.critical(stacktrace_msg)
        logging.critical(exception_msg)

        # Write to exception log file
        exception_file_name = datetime.now().strftime('rf2-settings-widget_Exception_%Y-%m-%d_%H%M%S.log')
        exception_file = Path(get_settings_dir()) / exception_file_name

        with open(exception_file, 'w') as f:
            traceback.print_exception(etype, value, tb, file=f)

        cls.gui_msg = f'{stacktrace_msg}\n{exception_msg}'
        cls.event.set()

    @classmethod
    def set_exception(cls, e: BaseException):
        cls.exception_hook(type(e), e, e.__traceback__)

    @staticmethod
    def test_exception():
        a = 1 / 0

    @staticmethod
    def exception_event_loop():
        if AppExceptionHook.produce_exception:
            AppExceptionHook.produce_exception = False

            @capture_app_exceptions
            def test_exception():
                AppExceptionHook.test_exception()
            test_exception()

        if AppExceptionHook.event.is_set():
            logging.debug('Reporting App exception to front end')
            eel.app_exception(AppExceptionHook.gui_msg)
            AppExceptionHook.event.clear()


def capture_app_exceptions(func):
    """ Decorator to capture exceptions at app level """
    if not FROZEN:
        return func

    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            AppExceptionHook.set_exception(e)

    return func_wrapper


def execute_powershell_cmd(cmd: str) -> Tuple[int, Union[bytes, str], Union[bytes, str]]:
    p = sp.Popen(['powershell', cmd], **subprocess_args())
    out, err = p.communicate(timeout=5.0)

    if out:
        logging.debug('Powershell output: %s', out)
    if err:
        logging.error('Powershell error output: %s', err)

    return p.returncode, out, err


def create_shortcut(executable_path: Path, working_directory: Path, shortcut_location: Path,
                    arguments: str = ''):
    """ Create a Windows .lnk ShortCut file with powershell

    $Shell = New-Object -ComObject ("WScript.Shell")
    $ShortCut = $Shell.CreateShortcut($env:USERPROFILE + "\Desktop\Your Shortcut.lnk")
    $ShortCut.TargetPath="yourexecutable.exe"
    $ShortCut.Arguments="-arguementsifrequired"
    $ShortCut.WorkingDirectory = "c:\your\executable\folder\path";
    $ShortCut.WindowStyle = 1;
    $ShortCut.Hotkey = "CTRL+SHIFT+F";
    $ShortCut.IconLocation = "yourexecutable.exe, 0";
    $ShortCut.Description = "Your Custom Shortcut Description";
    $ShortCut.Save()

    :param executable_path: Path to the executable
    :param working_directory: Path to the working dir, appearing as "Start in" parameter in shortcut properties
    :param shortcut_location: Path to where to save the shortcut
    :param arguments: Additional arguments provided to the executable
    :return:
    """
    shell = '$Shell = New-Object -ComObject ("WScript.Shell")'
    loc = f'$ShortCut = $Shell.CreateShortcut("{str(WindowsPath(shortcut_location))}")'
    target = f'$ShortCut.TargetPath="{str(WindowsPath(executable_path))}"'
    arguments = f'$ShortCut.Arguments="{arguments}"'
    cwd = f'$ShortCut.WorkingDirectory = "{str(WindowsPath(working_directory))}"'

    cmd = f'{shell};{loc};{target};{arguments};{cwd};$ShortCut.Save()'

    return_code, _, _ = execute_powershell_cmd(cmd)
    return False if return_code != 0 else True


def start_lnk_from_powershell(shortcut: Path):
    cmd = f'Invoke-Item -Path "{str(WindowsPath(shortcut))}"'
    return_code, _, _ = execute_powershell_cmd(cmd)
    return False if return_code != 0 else True


# https://github.com/pyinstaller/pyinstaller/wiki/Recipe-subprocess
# Create a set of arguments which make a ``subprocess.Popen`` (and
# variants) call work with or without Pyinstaller, ``--noconsole`` or
# not, on Windows and Linux. Typical use::
#
#   subprocess.call(['program_to_run', 'arg_1'], **subprocess_args())
#
# When calling ``check_output``::
#
#   subprocess.check_output(['program_to_run', 'arg_1'],
#                           **subprocess_args(False))
def subprocess_args(include_stdout=True, cwd=None):
    # The following is true only on Windows.
    if hasattr(sp, 'STARTUPINFO'):
        # On Windows, subprocess calls will pop up a command window by default
        # when run from Pyinstaller with the ``--noconsole`` option. Avoid this
        # distraction.
        si = sp.STARTUPINFO()
        si.dwFlags |= sp.STARTF_USESHOWWINDOW
        # Windows doesn't search the path by default. Pass it an environment so
        # it will.
        env = os.environ
    else:
        si = None
        env = None

    # ``subprocess.check_output`` doesn't allow specifying ``stdout``::
    #
    #   Traceback (most recent call last):
    #     File "test_subprocess.py", line 58, in <module>
    #       **subprocess_args(stdout=None))
    #     File "C:\Python27\lib\subprocess.py", line 567, in check_output
    #       raise ValueError('stdout argument not allowed, it will be overridden.')
    #   ValueError: stdout argument not allowed, it will be overridden.
    #
    # So, add it only if it's needed.
    if include_stdout:
        ret = {'stdout': sp.PIPE}
    else:
        ret = {}

    # On Windows, running this from the binary produced by Pyinstaller
    # with the ``--noconsole`` option requires redirecting everything
    # (stdin, stdout, stderr) to avoid an OSError exception
    # "[Error 6] the handle is invalid."
    ret.update({'stdin': sp.PIPE,
                'stderr': sp.PIPE,
                'startupinfo': si,
                'env': env,
                'cwd': cwd})
    return ret


def create_js_pygame_event_dict(joy_dict: dict, joy_event) -> dict:
    """ Create a JS friendly dictionary from a pygame joystick event """
    name, guid = 'Keyboard', 'Keyboard'
    button, hat, axis, value = None, None, None, None
    j = joy_dict.get(joy_event.instance_id)

    if joy_event.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYHATMOTION, pygame.JOYAXISMOTION):
        if j:
            name, guid = j.get_name(), j.get_guid()
        else:
            name, guid = 'Unknown', '-1'
    if joy_event.type in (pygame.JOYBUTTONUP, pygame.JOYBUTTONDOWN):
        button = joy_event.button
    elif joy_event.type == pygame.JOYHATMOTION:
        value, hat = list(joy_event.value), joy_event.hat
    elif joy_event.type == pygame.JOYAXISMOTION:
        value, axis = joy_event.value, joy_event.axis

    return {'name': name, 'guid': guid, 'button': button,
            'hat': hat, 'axis': axis, 'value': value, 'type': joy_event.type}


def get_pygame_joy_dict():
    joy_dict = dict()
    if pygame.joystick.get_init():
        for j_id in range(pygame.joystick.get_count()):
            j = pygame.joystick.Joystick(j_id)
            j.init()
            joy_dict[j.get_instance_id()] = j

    return joy_dict


def create_js_joystick_device_list(device_dict: dict, joy_dict: dict = None) -> list:
    js_list = list()

    # -- Update from App Settings device dict
    if not joy_dict:
        joy_dict = get_pygame_joy_dict()

    # -- Update from PyGame data
    for guid, device in device_dict.items():
        device['connected'] = False
    for instance_id, j in joy_dict.items():
        if j.get_guid() in device_dict:
            device_dict[j.get_guid()]['connected'] = True
        else:
            device_dict[j.get_guid()] = {'name': j.get_name(), 'guid': j.get_guid(),
                                         'connected': True, 'watched': False}

    for guid, device in device_dict.items():
        js_list.append(device)

    return js_list


def percentile(data, percent: Union[int, float]):
    size = len(data)
    return data[int(math.ceil((size * percent) / 100)) - 1]


class AppAudioFx:
    confirm = "audioConfirm"
    ping = "audioPing"
    indicator = "audioIndicator"
    select = "audioSelect"
    cute_select = "audioCuteSelect"
    switch = "audioSwitch"
    switch_on = "audioSwitchOn"
    switch_off = "audioSwitchOff"
    flash = "audioFlash"

    @classmethod
    def play_audio(cls, audio_fx_id: str):
        if not audio_fx_id:
            return
        eel.play_audio(audio_fx_id)


class SizeUnit(enum.Enum):
    BYTES = 1
    KB = 2
    MB = 3
    GB = 4


def convert_unit(size_in_bytes, unit):
    """ Convert the size from bytes to other units like KB, MB or GB"""
    size_in_bytes = int(size_in_bytes)
    if unit == SizeUnit.KB:
        return size_in_bytes / 1024
    elif unit == SizeUnit.MB:
        return size_in_bytes / (1024 * 1024)
    elif unit == SizeUnit.GB:
        return size_in_bytes / (1024 * 1024 * 1024)
    else:
        return size_in_bytes


def rfactor_process_with_id_exists(pid: Optional[int]) -> bool:
    if not pid:
        return False

    try:
        p = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return False
    if p.name().lower().startswith('rfactor2.exe'):
        return True


def get_widest(str_list, space=3):
    max_len = 0
    for v in str_list:
        max_len = max(max_len, len(v))
    return max_len + space


def pad_string(s, length, align_right=False):
    if align_right:
        return s.rjust(length, ' ')
    return s.ljust(length, ' ')


def greenlet_sleep(seconds, close_event: gevent.event.Event = None):
    # -- Normal sleep event
    if seconds < 10:
        gevent.sleep(seconds)
        return

    # -- Longer sleep will also listen for CLOSE event
    start = time.time()
    while time.time() - start < seconds:
        if close_event and close_event.is_set():
            break
        gevent.sleep(5.0)


def get_registry_values_as_dict(key: "registry.HKEYType") -> Dict[str, Dict[str, Any]]:
    """Enumerate all registry values in the given key and return them as dictionary
    :returns: {"RegistryValueName": {"data": Value, "type": RegistryType as Int}}
    """
    values = dict()

    if not WINREG_AVAIL:
        return values

    for i in range(0, registry.QueryInfoKey(key)[1]):
        name, data, data_type = registry.EnumValue(key, i)
        values[name] = {"data": data, "type": data_type}

    return values


# returns the requested version information from the given file
#
# `what` is one of the predefined version information strings, such as
# "FileVersion" or "CompanyName"
#
# `language` should be an 8-character string combining both the language and
# codepage (such as "040904b0"); if None, the first language in the translation
# table is used instead
#
def get_version_string(filename, what, language=None):
    # VerQueryValue() returns an array of that for VarFileInfo\Translation
    #
    class LANGANDCODEPAGE(ctypes.Structure):
        _fields_ = [("wLanguage", ctypes.c_uint16), ("wCodePage", ctypes.c_uint16)]

    wstr_file = ctypes.wstring_at(filename)

    # getting the size in bytes of the file version info buffer
    size = ctypes.windll.version.GetFileVersionInfoSizeW(wstr_file, None)
    if size == 0:
        raise ctypes.WinError()

    buffer = ctypes.create_string_buffer(size)

    # getting the file version info data
    if ctypes.windll.version.GetFileVersionInfoW(wstr_file, None, size, buffer) == 0:
        raise ctypes.WinError()

    # VerQueryValue() wants a pointer to a void* and DWORD; used both for
    # getting the default language (if necessary) and getting the actual data
    # below
    value = ctypes.c_void_p(0)
    value_size = ctypes.c_uint(0)

    if language is None:
        # file version information can contain much more than the version
        # number (copyright, application name, etc.) and these are all
        # translatable
        #
        # the following arbitrarily gets the first language and codepage from
        # the list
        ret = ctypes.windll.version.VerQueryValueW(
            buffer, ctypes.wstring_at(r"\VarFileInfo\Translation"), ctypes.byref(value), ctypes.byref(value_size)
        )

        if ret == 0:
            raise ctypes.WinError()

        # value points to a byte inside buffer, value_size is the size in bytes
        # of that particular section

        # casting the void* to a LANGANDCODEPAGE*
        lcp = ctypes.cast(value, ctypes.POINTER(LANGANDCODEPAGE))

        # formatting language and codepage to something like "040904b0"
        language = "{0:04x}{1:04x}".format(lcp.contents.wLanguage, lcp.contents.wCodePage)

    # getting the actual data
    res = ctypes.windll.version.VerQueryValueW(
        buffer,
        ctypes.wstring_at("\\StringFileInfo\\" + language + "\\" + what),
        ctypes.byref(value),
        ctypes.byref(value_size),
    )

    if res == 0:
        raise ctypes.WinError()

    # value points to a string of value_size characters, minus one for the
    # terminating null
    return ctypes.wstring_at(value.value, value_size.value - 1)
