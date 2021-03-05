# -*- mode: python ; coding: utf-8 -*-
from types import ModuleType

try:
    import pygame
    pygame_avail = 1
except ImportError:
    pygame_avail = 0

from PyInstaller.utils.hooks import get_package_paths

block_cipher = None
excluded_modules = list()

# ----- define app name
APP_NAME = 'rF2-Settings-Widget'

# ----- locate eel.js
eel_js = get_package_paths('eel')[-1] + '\\eel.js'

# ----- App Icon
icon_file = './vue/src/assets/app_icon.ico'

if pygame_avail:
    # ---- pygame excludes
    required_pygame_modules = ('base', 'constants', 'color', 'colordict', 'event', 'version', 'rect', 'compat', 'rwobject',
                               'surflock', 'bufferproxy', 'math', 'joystick', 'key', 'mouse')
    for p in dir(pygame):
        if type(getattr(pygame, p)) is ModuleType and p not in required_pygame_modules:
            excluded_modules.append(f'pygame.{p}')

# ---- other excludes
excluded_modules += ['_ssl', 'cryptography']


a = Analysis(['app.py'],
             pathex=['D:\\Docs\\py\\rfvideosettings'],
             binaries=[],
             datas=[(eel_js, 'eel'), ('web', 'web'), ('rf2settings/default_presets', 'default_presets'),
                    ('build/version.txt', '.'), ('license.txt', '.'), ],
             hiddenimports=['bottle_websocket'],
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
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=['vcruntime140.dll', 'python38.dll', 'python.dll'],
               name=APP_NAME)