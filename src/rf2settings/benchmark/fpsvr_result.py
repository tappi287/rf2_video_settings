import csv
import statistics
from pathlib import Path
from typing import Optional, Tuple

from rf2settings.utils import pad_string, get_widest


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


def _get_setting_names_from_file_stem(file_stem: str) -> Tuple[str, str]:
    name, date = file_stem.split('_', 1)
    option, setting = name.split('-', 1)
    return option, setting


def _sort_results(results: dict) -> dict:
    file_idx = dict()
    ordered_results = dict()
    setting_order = {'Off': 0, 'Low': 1, 'Medium': 2, 'High': 3, 'Full': 4, 'Ultra': 5}

    for file_stem in results:
        option, setting = _get_setting_names_from_file_stem(file_stem)
        file_idx[f'{setting_order.get(setting, setting)}-{setting}_{option}'] = file_stem

    for file_stem in [file_idx[k] for k in sorted(file_idx)]:
        ordered_results[file_stem] = results.get(file_stem)

    return ordered_results


def print_fpsvr_results():
    result_dir = Path(r'C:\Users\tappe\Documents\rf2_settings_widget\benchmark_results')
    results = dict()

    for file in result_dir.glob('*.csv'):
        data = read_fps_vr_result(file)
        if data:
            results[file.stem] = data

    ordered_results = _sort_results(results)
    results, num_datapoints = dict(), dict()

    for file_stem, data in ordered_results.items():
        option, setting = _get_setting_names_from_file_stem(file_stem)
        setting = pad_string(setting, 6)

        if option not in results:
            results[option] = dict()
            num_datapoints[option] = 0
        num_datapoints[option] += len(data['GPU frametime'])

        results[option][setting] = {
            'GPU': statistics.mean(data['GPU frametime']),
            'GPU Median': statistics.median(data['GPU frametime']),
            # 'GPU 0.2': data['GPU frametime'].quantile(q=0.2),
            'CPU': statistics.mean(data['CPU frametime']),
            'CPU Median': statistics.median(data['CPU frametime']),
            # 'CPU 0.2': df['CPU frametime'].quantile(q=0.2),
        }

    # -- Add percentage change
    for option, setting_dict in results.items():
        prev_setting = str()

        percent_data, num_data = dict(), 0
        for setting, data in setting_dict.items():
            percent_data[setting] = dict()

            if not prev_setting:
                prev_setting = setting
                percent_data[setting]['GPU Change'] = 0.0
                percent_data[setting]['CPU Change'] = 0.0
                continue

            prev_data = setting_dict[prev_setting]
            p_gpu = (data['GPU'] * 100 / max(0.1, prev_data['GPU'])) - 100
            p_cpu = (data['CPU'] * 100 / max(0.1, prev_data['CPU'])) - 100
            percent_data[setting]['GPU Change'] = p_gpu
            percent_data[setting]['CPU Change'] = p_cpu

        for setting, data in percent_data.items():
            setting_dict[setting]['GPU Change'] = data['GPU Change']
            setting_dict[setting]['CPU Change'] = data['CPU Change']

    left_spacing, align_right = 8, True
    for option, setting_dict in results.items():
        print('\n')
        header_line = str()

        for setting, data in setting_dict.items():
            line = f'{setting}{" " * (left_spacing - len(setting))}'
            header = list(data.keys())

            # -- Get string values
            data_values = list()
            for key, value in data.items():
                if 'Change' in key:
                    v = f'{value:6.2f} %'
                else:
                    v = f'{value:6.2f} ms'
                if value == 0.0:
                    v = '-'
                data_values.append(v)

            # -- Print Header with data columns
            if not header_line:
                print(option)
                header_line = f'{" " * left_spacing}'
                for h in header:
                    header_line += pad_string(h, get_widest(data_values + [h], 4), align_right=align_right)
                print(header_line)

            # -- Print value lines
            for value, key in zip(data_values, data):
                line += pad_string(value, get_widest(data_values + [key], 4), align_right=align_right)

            print(line)
        print(f'*average frametimes [{num_datapoints[option]} datapoints]')


if __name__ == '__main__':
    print_fpsvr_results()
