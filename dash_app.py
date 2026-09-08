"""Thin compatibility entry point kept at the repo root: `python3 dash_app.py [options]` and wsgi.py's `import
dash_app` both still work. The implementation lives in the webapp/ package - see webapp/cli.py for the CLI and
webapp/server.py for the Dash app itself."""
from webapp.cli import main
from webapp.server import app

if __name__ == "__main__":
    main()
