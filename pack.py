from pathlib import Path
from subprocess import Popen
from rf2settings.globals import get_version
from private.sftp import Remote

VERSION = get_version()

REMOTE_DIR = 'packages/rf2settings'
LOCAL_FILE = f'dist/rf2settings-{VERSION}.tar.gz'
LOCAL_WHEEL = f'dist/rf2settings-{VERSION}-py3-none-any.whl'


def upload_release(pkg_file: Path) -> bool:
    if not pkg_file.exists():
        print('Can not upload package. File not found: ' + pkg_file.as_posix())
        return False

    sftp = Remote(REMOTE_DIR)
    if not sftp.connect():
        print('Could not connect to remote host!')
        return False

    if sftp.put(pkg_file):
        return True
    return False


def main():
    proc = Popen(['python', 'setup.py', 'sdist'], cwd=Path('.'))
    exitcode = proc.wait()

    if exitcode != 0:
        print('Error creating python package!')
        return

    if not upload_release(Path(LOCAL_FILE)):
        print('Error uploading package!')
        return
    print('\nPackage updated and uploaded.\n\n')

    print('Creating bdist wheel')
    proc = Popen(['python', 'setup.py', 'bdist_wheel'], cwd=Path('.'))
    exitcode = proc.wait()

    if exitcode != 0:
        print('Error creating python wheel!')
        return

    if not upload_release(Path(LOCAL_WHEEL)):
        print('Error uploading wheel!')
        return

    print('Created and uploaded package wheel. The End.')


if __name__ == '__main__':
    main()
