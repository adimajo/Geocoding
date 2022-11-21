"""
create app object
"""
import os

from flask import Flask
from flask import redirect
from flask import url_for
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
    csrf = CSRFProtect()
    app.config['JSON_SORT_KEYS'] = False
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "to_debug")  # nosec

    @app.errorhandler(404)
    def handle_404(error):
        return redirect(url_for('_use'))

    @app.route('/')
    def homepage():
        return redirect(url_for('_home'))

    api = Api(
        app=app,
        title='Geocoder',
        version=__version__,
        description='Geocoder pour la France',
        contact='adrien.ehrhardt@credit-agricole-sa.fr',
        decorators=[csrf.exempt],
        doc="/doc",
        default='mapi',
        default_label='Super API'
    )
    api.add_namespace(api_rest)
    csrf.init_app(app)
    return app


app = create_app()
