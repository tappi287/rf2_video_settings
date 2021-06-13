import logging
import os
import os.path
import re
import subprocess as sp
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Tuple, Union, Optional

import eel
import gevent.event

from .globals import get_settings_dir

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
    before_load_callback: Optional[callable] = None

    def to_js_object(self, export: bool = False):
        if self.before_load_callback:
            self.before_load_callback()

        js_dict = dict()
        for k, v in self.__dict__.items():
            if (export and k in self.export_skip_keys) or k in self.skip_keys:
                continue
            if k[:2] == '__' or callable(v):
                continue

            js_dict[k] = v
        return js_dict

    def from_js_dict(self, json_dict):
        for k, v in json_dict.items():
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
        if AppExceptionHook.event.is_set():
            logging.debug('Reporting App exception to front end')
            eel.app_exception(AppExceptionHook.gui_msg)
            AppExceptionHook.event.clear()


def capture_app_exceptions(func):
    """ Decorator to capture exceptions at app level """
    def func_wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
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
def subprocess_args(include_stdout=True):
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
                'env': env})
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
