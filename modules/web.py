import random

import eel


@eel.expose
def message():
    return f'A random message from Python: {random.random()}'
