"""
defines all routes

.. autosummary::
    get_jsoned_geocoded_data
    geocode_one
    geocode_file
"""
import json
from datetime import datetime

import pandas as pd
from Geocoding_utils import ADDRESS, POSTAL_CODE, CITY
from flask import jsonify
from flask import render_template, make_response
from flask import request
from flask_restx import Namespace, Resource

from geocoder import __version__
from geocoder.api.Geocoder import Geocoder

QUALITY = {'1': 'Successful',
           '2': 'Precise number was not found',
           '3': 'Precise number was not found and there was no number in the input',
           '4': 'Street was not found',
           '5': 'City was not found',
           '6': 'Nothing was found'}

api_rest = Namespace('')


@api_rest.route("/home")
class Home(Resource):
    """
    Render homepage

    Methods
    -------
    get:
        get method for Home resource: outputs the homepage

    """
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("index.html"), 200, headers)


@api_rest.route("/version")
class Version(Resource):
    """
    Flask resource to spit current version

    Methods
    -------
    get:
        get method for Version resource: outputs the current version of the stresspent

    """
    @api_rest.doc(responses={200: 'Version of the stresspent API'})
    @api_rest.doc(responses={500: 'All other server errors'})
    def get(self):
        response = jsonify(version=__version__)
        response.status_code = 200
        return response


@api_rest.route("/use")
class Use(Resource):
    """
    Render Use

    Methods
    -------
    get:
        get method for Use resource: shows how to use the API

    """
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("use_rest.html"), 200, headers)


def get_jsoned_geocoded_data(geocoder):
    output_json = {
        'uuid': geocoder.uuid,
        'geocoded_time': datetime.strftime(geocoder.get_geocoded_date_time(), '%Y-%m-%d %H:%M:%S.%f%z'),
        'api_version': __version__,
        'quality': QUALITY,
    }
    if geocoder.geocoded:
        output_json['data'] = geocoder.get_geocoded_data().to_dict('records')
    elif geocoder.has_errors():
        output_json['errors'] = geocoder.get_errors()
    else:
        output_json['errors'] = 'Data not geocoded !'
    return output_json


@api_rest.route("/geocode/<address>/<postal_code>/<city>", methods=["GET"])
class GeocodeOne(Resource):
    def get(self, address, postal_code, city):
        print(address)
        print(postal_code)
        print(city)
        geocoder = Geocoder(pd.DataFrame(data={ADDRESS: address, POSTAL_CODE: postal_code, CITY: city}, index=[0]))
        geocoder.geocode()
        return jsonify(get_jsoned_geocoded_data(geocoder))


@api_rest.route("/geocode_file", methods=["POST"])
class GeocodeFile(Resource):
    def post(self):
        json_as_str = request.get_json(force=True)
        try:
            data = json.loads(json_as_str)
        except (json.JSONDecodeError, TypeError):
            data = json.loads(json.dumps(json_as_str))
        data_to_geocode = pd.json_normalize(data)
        geocoder = Geocoder(data_to_geocode)
        geocoder.geocode()
        return jsonify(get_jsoned_geocoded_data(geocoder))
