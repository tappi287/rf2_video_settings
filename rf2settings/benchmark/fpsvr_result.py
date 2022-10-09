import csv
from pathlib import Path
from typing import Optional


def read_raw_frametimes_file_name(file, result_dir) -> Optional[Path]:
    with open(file, 'r') as f:
        lines = f.readlines()

    if not lines:
        return

    timestamp = str()
    for line in lines:
        if line.startswith('Frametimes/'):
            content = line.split('/')
            for c in content:
                if not c or not c[0].isdigit():
                    continue
                timestamp = c.replace('\n', '').replace(':', '_')
                break

    if not timestamp:
        return

    for f in result_dir.glob('*.csv'):
        if f.stem == f'Frametimes#Raw#{timestamp}':
            return f


def _get_fps_vr_columns(row, data):
    for field_name in row:
        if field_name == 'FPS':
            field_name = 'fps'
        data[field_name] = list()

    return data


def _get_fps_vr_detail_results(frametimes_reader) -> Optional[dict]:
    data, header_line = dict(), 2

    for idx, row in enumerate(frametimes_reader):
        # -- Decided whether this is fps vr data
        if idx == 0 and row[0] != 'sep=':
            return

        # -- Read header
        if idx < header_line:
            continue
        elif idx == header_line:
            _get_fps_vr_columns(row, data)
            continue

        # -- Read data
        for field_value, field_name in zip(row, data.keys()):
            field_value = field_value.replace('"', '')
            if field_value.isdigit():
                data[field_name].append(int(field_value))
            else:
                data[field_name].append(float(field_value))

    # -- Remove irrelevant data fields
    rem_field, fields_to_remove = False, list()
    for field_name in data:
        if field_name == 'CPU0':
            rem_field = True
        if rem_field:
            fields_to_remove.append(field_name)
            continue

    for field_name in fields_to_remove:
        if field_name in data:
            data.pop(field_name)

    # -- Convert Steam VR Time to PresentMon like TimeInSeconds
    initial_time, time_in_seconds = None, list()
    for timestamp in data.get('SteamVR Time'):
        if not initial_time:
            initial_time = timestamp
        time_in_seconds.append(timestamp - initial_time)
    data.pop('SteamVR Time')
    data['TimeInSeconds'] = time_in_seconds

    # -- Add PresentMon like frame time data
    if 'msBetweenPresents' not in data:
        frame_times = list()
        for fps in data.get('fps'):
            if not fps or fps == 0.0:
                frame_times.append(0.0)
                continue
            frame_times.append(1000 / fps)
        data['msBetweenPresents'] = frame_times

    return data


def read_fps_vr_result(file: Path) -> Optional[dict]:
    with open(file, newline='') as f:
        data = _get_fps_vr_detail_results(csv.reader(f))

    return data
