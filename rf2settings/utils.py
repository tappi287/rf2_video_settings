import json
import logging
import os
import os.path
import re
import subprocess as sp
from pathlib import Path, WindowsPath
from typing import Tuple, Union

try:
    import pygame
    pygame_avail = 1
except ImportError:
    pygame_avail = 0


def create_file_safe_name(filename: str) -> str:
    """ Replace any non alphanumeric characters from a string expect minus/underscore/period """
    return re.sub('[^\\w\\-_.]', '_', filename)


class JsonRepr:
    skip_keys = list()
    export_skip_keys = list()

    def to_js_object(self, export: bool = False):
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


def _create_js_pygame_event_dict(joy_dict: dict, joy_event):
    """ Create a JS friendly dictionary from a pygame joystick event """
    name, guid = 'Keyboard', 'Keyboard'
    button, hat, value = None, None, None
    j = joy_dict.get(joy_event.instance_id)

    if joy_event.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYHATMOTION, pygame.JOYAXISMOTION):
        if j:
            name, guid = j.get_name(), j.get_guid()
        else:
            name, guid = 'Unknown', '-1'
    if joy_event.type in (pygame.JOYBUTTONUP, pygame.JOYBUTTONDOWN):
        button = joy_event.button
    if joy_event.type == pygame.JOYHATMOTION:
        value, hat = joy_event.value, joy_event.hat

    return json.dumps({'name': name, 'guid': guid, 'button': button,
                       'hat': hat, 'value': value, 'type': joy_event.type}, ensure_ascii=False)