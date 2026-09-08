""" Creates the shared Dash `app` instance. Kept as its own leaf module - it imports nothing else from this package -
so that auth.py, layout.py and callbacks.py can each import `app` from here without an import cycle: server.py is the
only module that imports *them*, to trigger their callback/route registration (see server.py)."""
from dash import Dash

app = Dash(__name__, suppress_callback_exceptions=True)

