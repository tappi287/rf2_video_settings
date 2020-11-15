import sys
import json
import random
import logging

import eel

from modules.settings_model import Preset

# -- Log to Stdout keeping it short
logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M', level=logging.DEBUG)


@eel.expose
def message():
    return f'A random message from Python: {random.random()}'


@eel.expose
def get_presets():
    p = Preset()
    presets = [p.to_js()]
    return json.dumps(presets)


@eel.expose
def save_preset(preset_js_dict):
    p = Preset()
    p.from_js_dict(preset_js_dict)
    logging.debug('Saved Preset: %s', p.name)
