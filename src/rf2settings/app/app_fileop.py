import json
import logging
import string
import uuid
from ctypes import windll
from pathlib import Path
from typing import Union, List

import eel


def expose():
    """ Method required for eel to "see" this method """
    pass


def get_windows_drive_letters():
    drives = list()
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(str(letter))
        bitmask >>= 1
    return drives


class FileSystemNode:
    # Directories starting with this string will be excluded
    EXCLUDES = ("$", ".", "System Volume Information")

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        self.id = str(uuid.uuid4())

    def children(self) -> List['FileSystemNode']:
        return [FileSystemNode(c) for c in self.path.iterdir() if not c.name.startswith(self.EXCLUDES)]

    def children_to_dict(self, recursive=False) -> List[dict]:
        """ Return the first children/subdirectories with or without recurring further into subdirectories """
        return [c.to_dict(no_recurse=not recursive) for c in self.children()]

    def to_dict(self, no_recurse=False):
        """ Convert this node to an JSON serializable dict """
        child_data = list() if no_recurse else sorted(self.children_to_dict(), key=lambda c: not c['is_dir'])

        return {
            'path': self.path.as_posix(),
            'name': self.path.name or self.path.drive,
            'id': self.id,
            'children': child_data,
            'is_dir': self.path.is_dir(),
            'documents': [c for c in child_data if not c["is_dir"]]
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)


@eel.expose
def list_directory(base_path: str):
    # -- Check for valid path
    if not base_path:
        return json.dumps({'result': False, 'msg': 'No directory provided: {}'.format(base_path)})

    try:
        base_path = Path(base_path)
        if not base_path.exists() or not base_path.is_dir():
            return json.dumps({'result': False, 'msg': 'Not a directory: {}'.format(base_path)})
    except Exception as e:
        logging.error('Error reading provided base path: {}'.format(e))
        return json.dumps({'result': False, 'msg': 'Error reading provided base path: {}'.format(e)})

    try:
        data = FileSystemNode(base_path).to_dict()
    except Exception as e:
        logging.error('Error reading path: {}'.format(e))
        return json.dumps({'result': False, 'msg': 'Error reading path: {}'.format(e)})

    # -- Return base path as directory node including 1st level child paths
    return json.dumps(
        {
            'result': True,
            'data': data
        }
    )


@eel.expose
def list_root_directories():
    try:
        drives = get_windows_drive_letters()
    except Exception as e:
        logging.error('Trying to list system drives failed: {}'.format(e))
        return json.dumps({'result': False, 'msg': 'Trying to list system drives failed: {}'.format(e)})

    try:
        directories = list()
        for drive_letter in drives:
            p = Path(f'{drive_letter}:\\')
            if p.is_dir():
                directories.append(FileSystemNode(p).to_dict())
    except Exception as e:
        logging.error('Error accessing path: {}'.format(e))
        return json.dumps({'result': False, 'msg': 'Error accessing path: {}'.format(e)})

    return json.dumps(
        {
            'result': True,
            'data': directories
        }
    )
