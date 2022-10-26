from geocoder.api.app import get_app
from geocoder.api.port import PORT

app = get_app()

if __name__ == '__main__':  # pragma: no cover
    app.run(host='0.0.0.0', port=PORT, debug=False)  # nosec
