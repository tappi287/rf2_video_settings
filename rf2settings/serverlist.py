import concurrent.futures
import logging
import os
from typing import List, Optional, Union, Tuple

import a2s
from a2s import Player

from rf2settings.app_settings import AppSettings
from rf2settings.globals import RF2_APPID
from rf2settings.valve import master_server, NoResponseError

_SERVER_REGIONS = ['eu', 'na-east', 'na-west', 'na', 'sa', 'as', 'oc', 'af', 'rest']


class ServerList:
    timeout = 1.0    # Timeout per server info query
    workers = min(48, int(max(4, os.cpu_count()) * 3))  # Number of server info workers
    chunk_size = 8  # Max number of servers to query per worker
    transfer_chunk_size = chunk_size * 10  # Reduce update rate for a more responsive front end

    # Age in hours of a player instance we consider no longer valid
    skip_player_threshold_age = 8.0

    # Server info attributes we're interested in
    attributes = ('map_name', 'max_players', 'mod_version', 'version', 'protocol', 'password_protected', 'ping',
                  'platform', 'bot_count', 'player_count', 'protocol', 'server_name', 'server_type', 'steam_id',
                  'ip', 'port', 'players')

    def __init__(self, update_players: bool = False, only_favourites: bool = False):
        self.servers: List[dict] = list()
        self.update_players = update_players
        self.only_favourites = only_favourites

        _a2s_logger = logging.getLogger('a2s')
        _a2s_logger.setLevel(logging.INFO)

    def update(self, transfer_server_list_chunk: callable, report_progress: Optional[callable] = None):
        """ Acquire a complete list of available rFactor 2 Servers
            This will block until all worker threads are finished.
        """
        server_address_list = list()
        update_chunk_size = self.chunk_size

        # -- Get a list of IP:Port addresses from the Steam Master Server
        #    that run rFactor 2 Servers
        if not self.only_favourites:
            server_address_list = self.get_server_addresses()
            if not server_address_list:
                logging.error('Could not acquire server list from master server!')
                return

        if self.only_favourites:
            update_chunk_size = 1
            for favourite_id in AppSettings.server_favourites:
                fav_ip, fav_port = favourite_id.split(':')
                server_address_list.append((fav_ip, int(fav_port)))

        # -- Initial progress report
        _num_server = len(server_address_list)
        self.report_progress(report_progress, 1, 100)

        # -- Split server addresses into chunks for workers
        address_chunks: List[list] = list()
        while server_address_list:
            chunks = list()
            for i in range(min(update_chunk_size, len(server_address_list))):
                chunks.append(server_address_list.pop())
            address_chunks.append(chunks)

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            future_info = {executor.submit(self._get_server_info_worker, c,
                                           self.timeout, self.update_players): c for c in address_chunks}
            _transfer_chunk = list()

            for future in concurrent.futures.as_completed(future_info):
                address_chunk = future_info[future]
                try:
                    server_info_ls = future.result()
                except Exception as exc:
                    logging.error('Querying address chunk %s generated an exception: %s', address_chunk, exc)
                else:
                    if not server_info_ls:
                        continue

                    # -- Update server list
                    self.servers += server_info_ls

                    # -- Update transfer queue
                    _transfer_chunk += server_info_ls
                    if len(_transfer_chunk) > self.transfer_chunk_size:
                        transfer_server_list_chunk(_transfer_chunk)
                        _transfer_chunk = list()

                    # -- Report progress
                    self.report_progress(report_progress, len(self.servers), _num_server)
                    logging.debug('Read x%s servers for address chunk %s', len(server_info_ls), address_chunk)

        # -- Transfer remaining chunk
        if _transfer_chunk:
            transfer_server_list_chunk(_transfer_chunk)
            self.report_progress(report_progress, len(self.servers), _num_server)

    def update_single(self, address: Tuple[str, int]) -> Optional[dict]:
        server_info_ls = self._get_server_info_worker([address], self.timeout, full_update=True)

        if server_info_ls:
            return server_info_ls[0]

    @staticmethod
    def report_progress(report_progress: Optional[callable] = None, progress: int = 0, complete: int = 1):
        if report_progress is not None:
            report_progress(progress, complete)

    @classmethod
    def _source_info_to_server_dict(cls, server_info: a2s.SourceInfo, address: Optional[Union[tuple, str]] = None
                                    ) -> dict:
        """ Convert the Source Info to json friendly dict """
        server_id = f'0.0.0.0:00000'
        server_info_dict = dict()
        server_info_dict['id'] = server_id
        server_info_dict['password'] = ''

        if address:
            server_info_dict['address'] = address
            server_id = f'{address[0]}:{address[1]}'
            server_info_dict['id'] = server_id

        # -- Restore password information
        if server_id in AppSettings.server_passwords:
            server_info_dict['password'] = AppSettings.server_passwords.get(server_id)

        for attr in cls.attributes:
            if hasattr(server_info, attr):
                server_info_dict[attr] = getattr(server_info, attr)

        server_info_dict['ping'] = round(server_info_dict.get('ping', 0.999) * 1000)

        return server_info_dict

    @classmethod
    def _get_server_info_worker(cls, address_list, query_timeout: float = 1.0, full_update: bool = False) -> list:
        server_info_ls: List[dict] = list()

        for address in address_list:
            try:
                # -- Get Server info
                info = a2s.info(address, query_timeout)
                info.players = list()

                # -- Get Player Info if requested
                if info and full_update:
                    try:
                        players = a2s.players(address, query_timeout * 4)
                        info.players = cls._serialize_player_info(players)
                        info.player_count = len(info.players)
                    except Exception as exc:
                        logging.error('Error while querying for player info: %s', exc)

                # -- Remove AI from player count
                info.player_count = max(0, info.player_count - info.bot_count)

                # -- Serialize data to JSON dict
                if info:
                    server_info_ls.append(cls._source_info_to_server_dict(info, address))
            except Exception as exc:
                logging.error('Error while querying for server info: %s', exc)

        return server_info_ls

    @classmethod
    def _serialize_player_info(cls, players: List[Player]):
        player_list = list()

        for idx, player in enumerate(players):
            # Skip players older than threshold in hours
            if player.duration and (player.duration / 3600 > cls.skip_player_threshold_age):
                continue

            # Most player names are reported as index 0 with name ''
            player_list.append(player.name or f'Player_{idx:02d}')

        return list(player_list)

    @staticmethod
    def get_server_addresses(region='rest') -> list:
        with master_server.MasterServerQuerier() as msq:
            try:
                addresses = msq.find(region=region, appid=RF2_APPID)
            except NoResponseError:
                logging.error('Master Server request timed out.')

            return [a for a in addresses]
