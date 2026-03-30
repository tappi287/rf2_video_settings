"""Steam WebAPI client for fetching server list."""

import json
import logging
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Optional

from rf2settings.globals import RF2_APPID
from ..app_settings import AppSettings


def _get_steam_web_api_key() -> str:
    """Read STEAM_WEB_API_KEY from first line of .env file."""
    if AppSettings.app_preferences.get('steam_webapi_key'):
        return AppSettings.app_preferences.get('steam_webapi_key')
    env_path = Path(__file__).parent.parent.parent.parent / '.env'
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith('STEAM_WEB_API_KEY='):
                return first_line.split('=', 1)[1]
    except Exception as e:
        logging.error(f'Error reading STEAM_WEB_API_KEY from .env: {e}')
    return ''


def get_server_list(appid: Optional[str] = None, limit: int = 1000) -> dict:
    """
    Fetch server list from Steam WebAPI GetServerList endpoint.

    Args:
        appid: Steam AppID to filter by. Defaults to RF2_APPID from globals.
        limit: Maximum number of servers to retrieve. Defaults to 1000.

    Returns:
        dict: API response containing server list or error information.
    """
    if appid is None:
        appid = RF2_APPID

    api_key = _get_steam_web_api_key()
    if not api_key:
        logging.error('STEAM_WEB_API_KEY not found in .env')
        return {'error': 'API key not found'}

    # Filter format: \appid\365960
    filter_value = f'\\appid\\{appid}'

    params = {
        'key': api_key,
        'filter': filter_value,
        'limit': str(limit),
        'format': 'json'
    }

    query_string = urllib.parse.urlencode(params)
    url = f'https://api.steampowered.com/IGameServersService/GetServerList/v1/?{query_string}'

    logging.debug(f'Requesting Steam WebAPI: {url}')

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except urllib.error.HTTPError as e:
        logging.error(f'Steam WebAPI HTTP error: {e.code} - {e.reason}')
        return {'error': f'HTTP {e.code}', 'reason': str(e.reason)}
    except urllib.error.URLError as e:
        logging.error(f'Steam WebAPI URL error: {e.reason}')
        return {'error': 'Connection failed', 'reason': str(e.reason)}
    except json.JSONDecodeError as e:
        logging.error(f'Error parsing Steam WebAPI response: {e}')
        return {'error': 'Invalid JSON response', 'reason': str(e)}
    except Exception as e:
        logging.error(f'Unexpected error fetching server list: {e}')
        return {'error': 'Unexpected error', 'reason': str(e)}
