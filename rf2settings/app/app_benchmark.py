import json
import logging
from subprocess import Popen

import eel

from ..app_settings import AppSettings
from ..preset.preset_base import PRESET_TYPES
from ..preset.settings_model import BenchmarkSettings
from ..rf2benchmarkutils import read_present_mon_result, BenchmarkRun, BenchmarkQueue
from ..rf2events import StartBenchmarkEvent


def expose_benchmark_methods():
    pass


@eel.expose
def start_benchmark():
    logging.info('Requested rF2 Benchmark run.')
    StartBenchmarkEvent.set(True)


@eel.expose
def get_benchmark_results():
    p = AppSettings.present_mon_result_dir
    logging.debug('Looking up Benchmark Results: %s', p)
    results = list()

    for idx, f in enumerate(p.glob('*.csv')):
        try:
            logging.debug('Preparing Benchmark Result: %s', f)
            r = {'id': idx, 'name': f.name, 'data': read_present_mon_result(f)}
            results.append(r)
        except Exception as e:
            logging.error('Error reading Benchmark result file: %s %s', f, e)

    return json.dumps(sorted(results, key=lambda x: x.get('name'), reverse=True))


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
    logging.info('Saving benchmark Settings: %s', settings)
    benchmark_settings = BenchmarkSettings()
    benchmark_settings.from_js_dict(settings)
    AppSettings.benchmark_settings = benchmark_settings.to_js()
    AppSettings.save()

    return json.dumps({'result': True, })


@eel.expose
def get_benchmark_settings():
    benchmark_settings = BenchmarkSettings()
    benchmark_settings.from_js_dict(AppSettings.benchmark_settings)

    return json.dumps({'result': True, benchmark_settings.app_key: benchmark_settings.to_js(), })


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

    logging.info('Queued benchmark run: %s %s', preset_names, benchmark_settings.to_js(export=True))
    return json.dumps({'result': True, })


@eel.expose
def reset_benchmark_queue():
    BenchmarkQueue.reset()
    return json.dumps({'result': True, })
