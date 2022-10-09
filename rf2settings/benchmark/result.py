import csv
import json
import logging
import statistics
from pathlib import Path
from typing import Dict

from rf2settings.preset.preset import BasePreset, GraphicsPreset, SessionPreset
from rf2settings.preset.preset_base import load_preset
from rf2settings.benchmark.fpsvr_result import read_raw_frametimes_file_name, read_fps_vr_result
from rf2settings.utils import percentile


def read_results(file: Path, details: bool = False):
    if not file.exists():
        return dict()

    data = read_fps_vr_result(file)
    if not data:
        data = read_present_mon_result(file, details)

    if 'fps' not in data:
        data['fps'] = [1000 / i for i in data.get('msBetweenPresents')]

    # -- Add Statistics
    sorted_fps = sorted(data['fps'])
    data['fps99'] = percentile(sorted_fps, 99)
    data['fps98'] = percentile(sorted_fps, 98)
    data['fps002'] = percentile(sorted_fps, 0.2)
    data['fpsmean'], data['fpsmedian'] = statistics.mean(sorted_fps), statistics.median(sorted_fps)

    if not details:
        data.pop('msBetweenPresents')
        data.pop('fps')
        data.pop('TimeInSeconds')

    return data


def read_present_mon_result(file: Path, details: bool = False):
    required_fields = {'msUntilDisplayed', 'QPCTime', 'msUntilRenderComplete', 'msBetweenDisplayChange',
                       'Dropped', 'msInPresentAPI', 'TimeInSeconds', 'msBetweenPresents'}
    non_detail_fields = {'msBetweenPresents', }

    data = dict()
    with open(file, newline='') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if row[0].startswith('//'):
                # -- Skip comment rows
                continue
            if not data:
                # -- Assume first line as Header with column names
                for field_name in row:
                    data[field_name] = list()
                continue

            # -- Collect data for every row
            for field_value, field_name in zip(row, data.keys()):
                if not details and field_name not in non_detail_fields:
                    continue
                if field_value.replace('.', '', 1).isdigit():
                    field_value = float(field_value)
                if field_name in required_fields:
                    data[field_name].append(field_value)

    # -- Remove unnecessary fields
    for key in set(data.keys()):
        if key not in required_fields:
            data.pop(key)

    return data


def read_preset_result(result_file: Path) -> Dict[int, BasePreset]:
    presets = dict()
    gfx = (GraphicsPreset.preset_type, GraphicsPreset.prefix)
    ses = (SessionPreset.preset_type, SessionPreset.prefix)

    for preset_type, prefix in (gfx, ses):
        for f in result_file.parent.glob(f'{result_file.stem}*{prefix}.json'):
            logging.debug('Located result preset: %s', f.name)
            p = load_preset(f, preset_type)
            presets[preset_type] = None if not p else p.to_js()

    return presets


def read_result_settings(f: Path):
    settings, setting_file = dict(), f.parent / f'{f.stem}_settings.json'

    if setting_file.exists():
        try:
            with open(setting_file, 'r') as f:
                settings = json.loads(f.read())
        except Exception as e:
            logging.error('Error reading benchmark result settings file: %s', e)

    return settings
