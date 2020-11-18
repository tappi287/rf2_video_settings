# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import get_package_paths

block_cipher = None

# ----- define app name
APP_NAME = 'rF2-Settings-Widget'
# ----- locate eel.js
eel_js = get_package_paths('eel')[-1] + '\\eel.js'
# -----
icon_file = './vue/src/assets/app_icon.ico'

a = Analysis(['app.py'],
             pathex=['D:\\Docs\\py\\rfvideosettings'],
             binaries=[],
             datas=[(eel_js, 'eel'), ('web', 'web'), ('default_presets', 'default_presets')],
             hiddenimports=['bottle_websocket'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
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
               upx_exclude=[],
               name=APP_NAME)