import json

from typing import Union, List, Iterator

from pathlib import Path

import eel
import string
from ctypes import windll


def expose():
    """ empty method we import to have the exposed methods registered """
    pass


class TreeNode:
    def __init__(self, base_path: Path, read_children=False):
        self.path = base_path.as_posix()
        self.name = base_path.name
        self.expanded = False
        self.read_children = read_children

        if read_children:
            self.children: List[TreeNode] = self.get_children()
        else:
            self.children: List[TreeNode] = list()

    def get_children(self):
        return list(get_sub_directories(self.path, self.read_children))

    def serialize_children(self) -> List[dict]:
        return [t.serialize() for t in self.children]

    def serialize(self) -> dict:
        return {'path': self.path, 'name': self.name, 'children': self.serialize_children()}


def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1
    return drives


def get_root_directories(current_dir=None) -> Iterator[TreeNode]:
    drives = get_drives()

    for drive_letter in drives:
        p = Path(f'{drive_letter}:\\')
        yield TreeNode(p, read_children=True)


def get_sub_directories(directory: Union[Path, str], read_children=False) -> Iterator[TreeNode]:
    for sub_path in Path(directory).iterdir():
        if sub_path.is_dir():
            yield TreeNode(sub_path, read_children)


@eel.expose
def list_dirs(current_dir: str):
    if not current_dir:
        get_method = get_root_directories
    else:
        get_method = get_sub_directories

    tree_nodes = [t.serialize() for t in get_method(current_dir)]

    return json.dumps({'result': True, 'nodes': tree_nodes})
