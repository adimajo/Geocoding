"""
create app object
"""
import os

from flask import Flask
from flask_restx import Api
from flask_wtf.csrf import CSRFProtect

from geocoder import __version__
from geocoder.api.rest import api_rest
from geocoder.geocoding.datapaths import here


def create_app():
    """
    Creates the model serving Flask app

    :return: Flask app
    """
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(here), "site/templates"),
                static_folder=os.path.join(os.path.dirname(here), "site/static"))
    app.config['JSON_SORT_KEYS'] = False
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "to_debug")  # nosec
    app.register_blueprint(api_rest)
    api = Api(
        title='WhiteApp Flask',
        version=__version__,
        description='API blanche pour framework Flask sous Python',
    )
    csrf = CSRFProtect()
    csrf.init_app(app)
    api.init_app(app)
    return app


app = create_app()


def get_app():
    return app
