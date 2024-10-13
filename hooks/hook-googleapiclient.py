from pathlib import Path


def hook(hook_api):
    path = hook_api.__path__[0]
    base_path = Path(path) / 'discovery_cache' / 'documents'

    backup_dir = Path(__file__).parent / 'backup'
    backup_dir.mkdir(exist_ok=True)

    for f in base_path.iterdir():
        if not f.name.startswith('youtube'):
            f.replace(backup_dir / f.name)

    print('googleapiclient hook moved static cache files to backupdir')
