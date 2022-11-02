"""
A simple wsgi server
"""
import os

from geocoder.api.app import get_app

app = get_app()

if __name__ == '__main__':  # pragma: no cover
    app.run(host='0.0.0.0',  # nosec
            port="8000",  # nosec
            debug=os.environ.get("DEBUG", True))  # nosec
