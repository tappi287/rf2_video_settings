"""Functionality to enable OpenComposite (OpenVR-to-OpenXR runtime) for rFactor 2
or restore the original Valve OpenVR runtime.

OpenComposite (https://gitlab.com/znixian/OpenOVR) does not publish numbered releases.
For rFactor 2 the recommended build is the latest 64-bit build of the ``openxr`` branch,
which is auto built by AppVeyor on every push and served from the official download page.
Enabling it for rF2 uses the per-game installation method: the game's
``Bin64/openvr_api.dll`` is replaced with the OpenComposite dll while the original
Valve signed dll is backed up as ``openvr_api.dll.original``.
"""
import json
import logging
import shutil
import ssl
import urllib.request
from pathlib import Path
from typing import Optional

from ..globals import get_settings_dir
from ..mods.openxr import is_openvr_present, OPENVR_API_DLL
from ..rfactor import RfactorPlayer
from ..utils import capture_app_exceptions

OPENCOMPOSITE_DOWNLOAD_URL = 'https://znix.xyz/OpenComposite/download.php?arch=x64&branch=openxr'
OPENVR_API_BACKUP_DLL = 'openvr_api.dll.original'
OPENCOMPOSITE_CACHE_DIR_NAME = 'opencomposite'
OPENCOMPOSITE_CACHED_DLL = 'opencomposite_x64.dll'
DOWNLOAD_TIMEOUT = 60
PE_MAGIC_BYTES = b'MZ'


def opencomposite_cache_dir() -> Path:
    cache_dir = get_settings_dir() / OPENCOMPOSITE_CACHE_DIR_NAME
    if not cache_dir.exists():
        cache_dir.mkdir()
    return cache_dir


def opencomposite_cached_dll_path() -> Path:
    return opencomposite_cache_dir() / OPENCOMPOSITE_CACHED_DLL


def _get_bin64_dir() -> Optional[Path]:
    rf = RfactorPlayer(only_version=True)
    if not rf.version:
        logging.error('Could not locate rFactor 2 installation')
        return None

    bin_dir = rf.location / 'Bin64'
    if not bin_dir.is_dir():
        logging.error('Could not locate rFactor 2 Bin64 directory in %s', rf.location)
        return None
    return bin_dir


def _download_opencomposite_dll() -> bool:
    """Download the latest 64-bit OpenComposite build into the settings directory cache"""
    logging.info('Downloading latest OpenComposite x64 build from %s', OPENCOMPOSITE_DOWNLOAD_URL)
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        request = urllib.request.Request(OPENCOMPOSITE_DOWNLOAD_URL, headers={'User-Agent': 'rF2-Settings-Widget'})
        with urllib.request.urlopen(request, timeout=DOWNLOAD_TIMEOUT, context=ssl_context) as response:
            data = response.read()
    except Exception as e:
        logging.error(f'Error downloading OpenComposite: {e}')
        return False

    if not data or len(data) < 1024 or data[:2] != PE_MAGIC_BYTES:
        logging.error('Downloaded file does not look like a Windows PE binary')
        return False

    try:
        with open(opencomposite_cached_dll_path(), 'wb') as f:
            f.write(data)
    except OSError as e:
        logging.error(f'Error writing OpenComposite dll: {e}')
        return False

    logging.info('Stored OpenComposite dll at %s (%s bytes)', opencomposite_cached_dll_path(), len(data))
    return True


def _ensure_opencomposite_dll() -> bool:
    """Return cached OpenComposite dll or download the latest build if missing"""
    if opencomposite_cached_dll_path().is_file():
        return True
    return _download_opencomposite_dll()


def _opencomposite_status_data(bin_dir: Path) -> dict:
    dll = bin_dir / OPENVR_API_DLL
    backup = bin_dir / OPENVR_API_BACKUP_DLL
    original_present = is_openvr_present(bin_dir)

    return {
        'dll': dll.as_posix(),
        'backup': backup.as_posix(),
        'cached_dll': opencomposite_cached_dll_path().as_posix(),
        'original_present': original_present,
        'backup_present': backup.is_file(),
        'cached_dll_present': opencomposite_cached_dll_path().is_file(),
        'opencomposite_active': dll.is_file() and not original_present
    }


@capture_app_exceptions
def get_opencomposite_status():
    """Report current state of the OpenVR runtime in the rFactor 2 installation"""
    bin_dir = _get_bin64_dir()
    if bin_dir is None:
        return json.dumps({'result': False, 'msg': 'Could not locate rFactor 2 Bin64 directory'})

    return json.dumps({'result': True, 'msg': '', 'data': _opencomposite_status_data(bin_dir)})


@capture_app_exceptions
def download_opencomposite():
    """Download the latest 64-bit OpenComposite build into the local cache"""
    if _download_opencomposite_dll():
        msg = f'Downloaded latest OpenComposite x64 build to {opencomposite_cached_dll_path().as_posix()}'
        return json.dumps({'result': True, 'msg': msg})

    return json.dumps({'result': False, 'msg': 'Could not download latest OpenComposite x64 build'})


@capture_app_exceptions
def enable_opencomposite():
    """Back up the original openvr_api.dll and install the OpenComposite runtime dll"""
    bin_dir = _get_bin64_dir()
    if bin_dir is None:
        return json.dumps({'result': False, 'msg': 'Could not locate rFactor 2 Bin64 directory'})

    dll = bin_dir / OPENVR_API_DLL
    backup = bin_dir / OPENVR_API_BACKUP_DLL

    if not dll.is_file():
        return json.dumps({'result': False, 'msg': f'Could not locate {OPENVR_API_DLL} in {bin_dir.as_posix()}'})

    if not is_openvr_present(bin_dir):
        return json.dumps({'result': True, 'msg': 'OpenComposite is already active for rFactor 2'})

    if not backup.is_file():
        try:
            shutil.copy2(dll, backup)
        except OSError as e:
            return json.dumps({'result': False, 'msg': f'Could not back up original {OPENVR_API_DLL}: {e}'})
        logging.info('Backed up original OpenVR runtime dll to %s', backup.as_posix())

    if not _ensure_opencomposite_dll():
        return json.dumps({'result': False, 'msg': 'Could not download latest OpenComposite x64 build'})

    try:
        shutil.copy2(opencomposite_cached_dll_path(), dll)
    except OSError as e:
        return json.dumps({'result': False, 'msg': f'Could not install OpenComposite dll: {e}'})

    logging.info('Installed OpenComposite runtime dll at %s', dll.as_posix())
    return json.dumps({'result': True, 'msg': 'OpenComposite enabled for rFactor 2'})


@capture_app_exceptions
def restore_original_openvr():
    """Restore the original Valve openvr_api.dll from the .original backup"""
    bin_dir = _get_bin64_dir()
    if bin_dir is None:
        return json.dumps({'result': False, 'msg': 'Could not locate rFactor 2 Bin64 directory'})

    dll = bin_dir / OPENVR_API_DLL
    backup = bin_dir / OPENVR_API_BACKUP_DLL

    if is_openvr_present(bin_dir):
        return json.dumps({'result': True, 'msg': 'Original OpenVR runtime is already active'})

    if not backup.is_file():
        msg = (f'No backup of the original {OPENVR_API_DLL} found in {bin_dir.as_posix()}. '
               f'Reinstall rFactor 2 via Steam to restore the original OpenVR runtime.')
        return json.dumps({'result': False, 'msg': msg})

    try:
        shutil.copy2(backup, dll)
    except OSError as e:
        return json.dumps({'result': False, 'msg': f'Could not restore original {OPENVR_API_DLL}: {e}'})

    logging.info('Restored original OpenVR runtime dll at %s', dll.as_posix())
    return json.dumps({'result': True, 'msg': 'Original OpenVR runtime restored'})
