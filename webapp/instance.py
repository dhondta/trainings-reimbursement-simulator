""" Creates the shared Dash `app` instance, styled with the Bootstrap theme from config. Kept as a leaf module - it
imports nothing else from this package but config (itself a leaf) - so that auth.py, layout.py and callbacks.py can each
import `app` from here without an import cycle: server.py is the only module that imports *them*, to trigger their
callback/route registration (see server.py)."""
from dash import Dash

from . import config

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[config.THEME, config.ICONS])

