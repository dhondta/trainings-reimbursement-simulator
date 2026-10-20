""" Creates the shared Dash `app` instance, styled with the Bootstrap theme from config. Kept as a leaf module - it
imports nothing else from this package but config (itself a leaf) - so that auth.py, layout.py and callbacks.py can each
import `app` from here without an import cycle: server.py is the only module that imports *them*, to trigger their
callback/route registration (see server.py)."""
from dash import Dash

from . import config

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[config.THEME, config.ICONS])
# The color mode is set before the page renders, so that night mode doesn't flash the light one first: as last chosen
#  with the toggle (kept by the browser, see the theme-choice store in layout.py), the system's preference otherwise.
app.index_string = app.index_string.replace("{%css%}", """{%css%}
        <script>
            (function () {
                var choice = null;
                try { choice = JSON.parse(localStorage.getItem("theme-choice")); } catch (e) {}
                if (choice !== "light" && choice !== "dark")
                    choice = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
                document.documentElement.setAttribute("data-bs-theme", choice);
            })();
        </script>""")

