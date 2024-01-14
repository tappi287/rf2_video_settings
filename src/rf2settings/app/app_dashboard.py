import eel

from . import app_dashboard_fn


def expose_dashboard_methods():
    """ empty method we import to have the exposed methods registered """
    pass


@eel.expose
def get_rf_driver():
    return app_dashboard_fn.get_rf_driver()
