from .app_main import expose_main_methods
from .app_graphics import expose_graphics_methods
from .app_multiplayer import expose_multiplayer_methods

# -- Make sure eel methods are exposed at start-up
expose_main_methods()
expose_graphics_methods()
expose_multiplayer_methods()
