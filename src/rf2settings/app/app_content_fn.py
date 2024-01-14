import json
import logging

from ..app_settings import AppSettings
from ..rf2command import CommandQueue, Command
from ..rf2connect import RfactorState
from ..utils import capture_app_exceptions


@capture_app_exceptions
def get_content():
    if not AppSettings.content:
        return json.dumps({'result': False, 'msg': 'No rFactor 2 content listed. Start the game at least once to '
                                                   'populate the content list.'})
    content = AppSettings.content

    # -- Handle post v1124 Series entries
    for series in content.get('series'):
        if series.get('signature'):
            series['id'] = series.get('signature')

    # -- Group Cars by Manufacturer and Model
    content['manufacturer'], content['model'] = list(), list()
    m_set, c_set = set(), set()
    for car in content.get('cars', list()):
        manufacturer, model = car.get('manufacturer'), car.get('fullPathTree')
        if manufacturer not in m_set:
            content['manufacturer'].append({'id': manufacturer, 'shortName': manufacturer, 'name': manufacturer})
        if model not in c_set:
            content['model'].append({'id': model, 'manufacturer': manufacturer, 'shortName': model, 'name': model})
        m_set.add(manufacturer)
        c_set.add(model)

    # -- Group Tracks by Location
    content['location'], content['layout'] = list(), list()
    loc_set = set()
    for track in content.get('tracks', list()):
        location, layout = track.get('shortName'), track.get('name')
        if location not in loc_set:
            content['location'].append({'id': location, 'shortName': location, 'name': location})
        content['layout'].append({'id': layout, 'location': location, 'shortName': layout, 'name': layout,
                                  'track_id': track.get('id')})
        loc_set.add(location)

    content['manufacturer'] = sorted(content['manufacturer'], key=lambda e: e['name'])
    content['location'] = sorted(content['location'], key=lambda e: e['name'])

    logging.debug('Collected content dict for FrontEnd:'
                  f'Series: {len(content["series"])} Tracks: {len(content["tracks"])} '
                  f'Location: {len(content["location"])} Layouts: {len(content["layout"])} '
                  f'Manufacturer: {len(content["manufacturer"])} Models: {len(content["model"])} '
                  f'Cars: {len(content["cars"])}')

    return json.dumps({'result': True, 'content': content, 'selected': AppSettings.content_selected})


@capture_app_exceptions
def refresh_content():
    logging.debug('Queuing set/get content requests for a content refresh.')
    # -- Wait for Ui
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=120))

    # -- Switch to All Tracks & Cars Series
    selected = AppSettings.content_selected
    selected['series'] = None  # Will trigger selection of All Tracks & Cars in CommandQueue
    selected['tracks'], selected['cars'] = None, None
    CommandQueue.append(Command(Command.set_content, data=selected, timeout=20))

    # -- Get Content
    CommandQueue.append(Command(Command.get_content, timeout=20))
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=60))

    # -- Quit Game
    CommandQueue.append(Command(Command.quit, timeout=30))
