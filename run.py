import sys
from subprocess import Popen
from pathlib import Path

from app import start_eel

# -- Create web dir
web = Path('.') / 'web'
if not web.exists():
    web.mkdir()

# -- Run npm and build web package
cd = Path('.') / 'vue'
cmd = ['npm', 'run', 'build']

p = Popen(args=cmd, shell=True, cwd=cd.as_posix())
p.wait()
if p.returncode != 0:
    print('Build Web App failed.')
    sys.exit()

# -- Start app
start_eel(npm_serve=False)
