import json
import logging
from pathlib import Path
from subprocess import Popen

import eel

from ..app_settings import AppSettings
from ..preset.preset import GraphicsPreset, SessionPreset
from ..preset.preset_base import PRESET_TYPES
from ..preset.settings_model import BenchmarkSettings
from ..rf2benchmarkutils import read_present_mon_result, BenchmarkRun, BenchmarkQueue, read_preset_result
from ..rf2events import StartBenchmarkEvent


def expose_benchmark_methods():
    pass


@eel.expose
def start_benchmark():
    logging.info('Requested rF2 Benchmark run.')
    StartBenchmarkEvent.set(True)


def _read_result_settings(f: Path):
    settings, setting_file = dict(), f.parent / f'{f.stem}_settings.json'

    if setting_file.exists():
        try:
            with open(setting_file, 'r') as f:
                settings = json.loads(f.read())
        except Exception as e:
            logging.error('Error reading benchmark result settings file: %s', e)

    return settings


@eel.expose
def get_benchmark_results():
    p = AppSettings.present_mon_result_dir
    logging.debug('Looking up Benchmark Results: %s', p)
    results = list()

    for idx, f in enumerate(p.glob('*.csv')):
        try:
            logging.debug('Preparing Benchmark Result: %s', f)
            r = {'id': idx, 'name': f.name,
                 'data': read_present_mon_result(f, details=False),
                 'settings': _read_result_settings(f)}

            results.append(r)
        except Exception as e:
            logging.error('Error reading Benchmark result file: %s %s', f, e)

    return json.dumps(sorted(results, key=lambda x: x.get('name'), reverse=True))


@eel.expose
def get_benchmark_result_details(result_file_name: str):
    logging.debug('Looking up detailed Benchmark Results for: %s', result_file_name)

    p, data, presets = AppSettings.present_mon_result_dir, dict(), dict()
    for idx, f in enumerate(p.glob('*.csv')):
        if f.name != result_file_name:
            continue
        logging.debug('Reading detailed Benchmark Result: %s', f)
        data = read_present_mon_result(f, details=True)
        presets = read_preset_result(f)

    if data:
        return json.dumps({'result': True, 'data': data,
                           'gfxPreset': presets.get(GraphicsPreset.preset_type),
                           'sesPreset': presets.get(SessionPreset.preset_type)})

    logging.debug('Could not locate detailed Benchmark Result: %s', result_file_name)
    return json.dumps({'result': False, 'data': data, 'gfxPreset': None, 'sesPreset': None})


@eel.expose
def open_result_folder():
    result_path = AppSettings.present_mon_result_dir
    if result_path is None:
        return
    logging.info('Opening folder: %s', result_path)
    Popen(f'explorer /n,"{result_path}"')


@eel.expose
def delete_benchmark_result(name: str):
    p = AppSettings.present_mon_result_dir
    result_path = p / name

    # -- Remove Json Preset files
    for f in p.glob(f'{result_path.stem}*.json'):
        f.unlink()

    # -- Remove Result CSV
    if result_path.exists():
        result_path.unlink()


@eel.expose
def save_benchmark_settings(settings):
    benchmark_settings = BenchmarkSettings()
    benchmark_settings.from_js_dict(settings)
    AppSettings.benchmark_settings = benchmark_settings.to_js(export=True)
    logging.info('Saving benchmark Settings: %s', AppSettings.benchmark_settings)
    AppSettings.save()

    return json.dumps({'result': True, })


@eel.expose
def get_benchmark_settings():
    benchmark_settings = BenchmarkSettings()
    benchmark_settings.from_js_dict(AppSettings.benchmark_settings)

    return json.dumps({'result': True, benchmark_settings.app_key: benchmark_settings.to_js(), })


@eel.expose
def get_benchmark_queue():
    logging.debug('Providing benchmark queue to FrontEnd: %s', len(BenchmarkQueue.queue))
    return json.dumps({'result': True,
                       'queue': [{
                           'id': r.id, 'presets': [p.name for p in r.presets],
                           'replay': getattr(r.settings.get_option('Replay'), 'value', 'None')
                       } for r in BenchmarkQueue.queue],
                       })


@eel.expose
def queue_benchmark_run(preset_js_dict_list, settings):
    """ Queue a preset to the Benchmark Queue """
    r, preset_names = BenchmarkRun(), list()

    for preset_js_dict in preset_js_dict_list:
        # -- Get preset type and create an instance of it, fallback to GraphicsPreset
        p = PRESET_TYPES.get(preset_js_dict.get('preset_type', 0))()

        # -- Read options from js_dict
        p.from_js_dict(preset_js_dict)
        r.presets.append(p)
        preset_names.append(p.name)

    benchmark_settings = BenchmarkSettings()
    benchmark_settings.from_js_dict(settings)

    r.settings = benchmark_settings
    BenchmarkQueue.append(r)

    logging.info('Queued benchmark run: %s %s %s', r.id, preset_names, benchmark_settings.to_js(export=True))
    return json.dumps({'result': True, 'id': r.id})


@eel.expose
def remove_from_benchmark_queue(entry_id: int):
    if BenchmarkQueue.remove(entry_id):
        logging.info('Removed Benchmark Run %s from Queue', entry_id)
        return json.dumps({'result': True, 'id': entry_id})
    else:
        msg = f'Could not find Benchmark Run {entry_id} in Queue for removal'
        logging.error(msg)
        return json.dumps({'result': False, 'msg': msg, 'id': entry_id})


@eel.expose
def reset_benchmark_queue():
    BenchmarkQueue.reset()
    return json.dumps({'result': True, })
