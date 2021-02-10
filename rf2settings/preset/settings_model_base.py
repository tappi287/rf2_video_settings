from typing import Dict, Type

from . import settings_model
from ..globals import find_subclasses

OPTION_CLASSES: Dict[str, Type[settings_model.BaseOptions]] = dict()
for name, opt_class in find_subclasses(settings_model, settings_model.BaseOptions):
    OPTION_CLASSES[opt_class.app_key] = opt_class
del opt_class
