import logging
from pathlib import Path
from subprocess import Popen

import requests

from modules.globals import get_version, GIT_RELEASE_URL, UPDATE_INSTALL_FILE, get_settings_dir


class GitHubUpdater:
    downloaded_setup = Path()

    def __init__(self):
        self.version = get_version()
        self.git_version = ''
        self.download_url = ''

    def is_current_version(self) -> bool:
        r = requests.get(GIT_RELEASE_URL)
        if not r.ok:
            logging.error('Could not get GitHub release version. %s', r.status_code)
            return True

        try:
            response_dict = r.json()
        except ValueError as e:
            logging.error('GitHub response not in json: %s', e)
            return True

        self.git_version = response_dict.get('tag_name', '0.0.0')

        if self.git_version > self.version:
            self._get_download_url(response_dict)
            return False

        return True

    def download_update(self) -> bool:
        r = requests.get(self.download_url)
        dl_dir = Path.home() / 'Downloads'
        if not dl_dir.exists():
            dl_dir = get_settings_dir()

        try:
            installer_file = dl_dir / UPDATE_INSTALL_FILE.format(version=self.git_version)

            with open(installer_file, 'wb') as f:
                f.write(r.content)

            GitHubUpdater.downloaded_setup = installer_file
            return True
        except Exception as e:
            logging.error('Error saving update installer: %s', e)

        return False

    @staticmethod
    def execute_update_setup() -> bool:
        args = [GitHubUpdater.downloaded_setup.as_posix(), '/SILENT', '/CLOSEAPPLICATIONS', '/RESTARTAPPLICATIONS']
        try:
            Popen(args)
            logging.info('Running Update Installer: %s', args)
        except Exception as e:
            logging.error('Could not run update installer. %s', e)
            return False

        return True

    def _get_download_url(self, response_dict):
        try:
            self.download_url = response_dict['assets'][0]['browser_download_url']
        except Exception as e:
            logging.error('Could not find release donwload url: %s', e)
