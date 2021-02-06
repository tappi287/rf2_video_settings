from .app.app_dashboard import expose_dashboard_methods
from .app.app_main import expose_main_methods
from .app.app_graphics import expose_graphics_methods
from .app.app_multiplayer import expose_multiplayer_methods
from .app.app_presets import expose_preset_methods

# -- Make sure eel methods are exposed at start-up

expose_main_methods()
expose_dashboard_methods()
expose_graphics_methods()
expose_multiplayer_methods()
expose_preset_methods()
