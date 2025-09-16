import json
import logging
from pathlib import Path

import eel

from rf2settings.rf2results import RfactorResults
from rf2settings.utils import capture_app_exceptions


def expose_results_methods():
    pass


@eel.expose
def get_result_file(file_name: str):
    return _get_result_file_fn(file_name or str())


@capture_app_exceptions
def _get_result_file_fn(file_name: str):
    xml_file = Path(file_name)
    if not xml_file.is_file():
        json.dumps({"result": False, "msg": "File not found"})

    try:
        race_result = RfactorResults(xml_file)
    except Exception as e:
        logging.exception(e)
        return json.dumps({"result": False, "msg": str(e)})

    logging.info(f"Providing result data for {xml_file.name}")
    return json.dumps({"result": True, "data": race_result.to_js_object()})
