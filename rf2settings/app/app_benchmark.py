import json
import logging
from subprocess import Popen

import eel

from rf2settings.app_settings import AppSettings
from rf2settings.preset.presets_dir import get_user_presets_dir
from rf2settings.preset.settings_model import BenchmarkSettings
from rf2settings.rf2benchmark import RfactorBenchmark
from rf2settings.rf2events import StartBenchmarkEvent


def expose_benchmark_methods():
    pass


@eel.expose
def start_benchmark():
    logging.info('Requested rF2 Benchmark run.')
    StartBenchmarkEvent.set(True)


@eel.expose
def get_benchmark_results():
    p = RfactorBenchmark.present_mon_result_dir
    logging.debug('Looking up Benchmark Results: %s', p)
    results = list()

    for idx, f in enumerate(p.glob('*.csv')):
        try:
            logging.debug('Preparing Benchmark Result: %s', f)
            r = {'id': idx, 'name': f.name, 'data': RfactorBenchmark.read_present_mon_result(f)}
            results.append(r)
        except Exception as e:
            logging.error('Error reading Benchmark result file: %s %s', f, e)

    return json.dumps(sorted(results, key=lambda x: x.get('name'), reverse=True))


@eel.expose
def open_result_folder():
    result_path = get_user_presets_dir() / 'benchmark_results'
    if result_path is None:
        return
    logging.info('Opening folder: %s', result_path)
    Popen(f'explorer /n,"{result_path}"')


@eel.expose
def delete_benchmark_result(name: str):
    result_path = get_user_presets_dir() / 'benchmark_results' / name
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
