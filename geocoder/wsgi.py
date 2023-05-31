"""
A simple wsgi server
"""
import os
import platform
from abc import ABC

from geocoder.api.provider import app

if platform.uname().system.lower() == 'linux':
    import gunicorn.app.base

    class StandaloneApplication(gunicorn.app.base.BaseApplication, ABC):

        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            config = {key: value for key, value in self.options.items()
                      if key in self.cfg.settings and value is not None}
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application


def runserver(options):
    if platform.uname().system.lower() == 'linux':
        bind = f"{options.pop('host')}:{options.pop('port')}"
        options.update({"bind": bind})
        StandaloneApplication(app, options).run()
    else:
        app.run(host=options["host"],  # nosec
                port=options["port"],  # nosec
                debug=os.environ.get("DEBUG", True))  # nosec


if __name__ == '__main__':  # pragma: no cover
    app.run(host='0.0.0.0',  # nosec
            port="8001",  # nosec
            debug=os.environ.get("DEBUG", True))  # nosec
