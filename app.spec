# -*- mode: python ; coding: utf-8 -*-
from types import ModuleType

try:
    import pygame
    pygame_avail = 1
except ImportError:
    pygame_avail = 0

from PyInstaller.utils.hooks import get_package_paths

block_cipher = None
excluded_modules = ['cryptography']

# ----- define app name
APP_NAME = 'rF2-Settings-Widget'

# ----- locate eel.js
eel_js = get_package_paths('eel')[-1] + '\\eel.js'

# ----- App Icon
icon_file = './vue/src/assets/app_icon.ico'


a = Analysis(['app.py'],
             pathex=['C:\\py\\rf_video_settings'],
             binaries=[],
             datas=[(eel_js, 'eel'), ('web', 'web'), ('rf2settings/default_presets', 'default_presets'),
                    ('build/version.txt', '.'), ('license.txt', '.'), ('data', 'data'),
                    ('bin/PresentMon-1.9.2-x64.exe', 'bin'), ],
             hiddenimports=['bottle_websocket', 'ssl', '_ssl'],
             hookspath=['hooks'],
             runtime_hooks=[],
             excludes=excluded_modules,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name=APP_NAME,
          icon=icon_file,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=['vcruntime140.dll', 'python38.dll', 'python.dll', 'python3.dll', 'python310.dll'],
               name=APP_NAME)
