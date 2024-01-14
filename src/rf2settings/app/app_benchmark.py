import eel

from . import app_benchmark_fn


def expose_benchmark_methods():
    pass


@eel.expose
def start_benchmark():
    return app_benchmark_fn.start_benchmark()


@eel.expose
def get_benchmark_results():
    return app_benchmark_fn.get_benchmark_results()


@eel.expose
def get_benchmark_result_details(result_file_name: str):
    return app_benchmark_fn.get_benchmark_result_details(result_file_name)


@eel.expose
def open_result_folder():
    return app_benchmark_fn.open_result_folder()


@eel.expose
def delete_benchmark_result(name: str):
    return app_benchmark_fn.delete_benchmark_result(name)


@eel.expose
def save_benchmark_settings(settings):
    return app_benchmark_fn.save_benchmark_settings(settings)


@eel.expose
def get_benchmark_settings():
    return app_benchmark_fn.get_benchmark_settings()


@eel.expose
def get_benchmark_queue():
    return app_benchmark_fn.get_benchmark_queue()


@eel.expose
def queue_benchmark_run(preset_js_dict_list, settings):
    return app_benchmark_fn.queue_benchmark_run(preset_js_dict_list, settings)


@eel.expose
def remove_from_benchmark_queue(entry_id: int):
    return app_benchmark_fn.remove_from_benchmark_queue(entry_id)


@eel.expose
def reset_benchmark_queue():
    return app_benchmark_fn.reset_benchmark_queue()
