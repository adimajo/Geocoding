import json
from datetime import datetime

import pandas as pd
from Geocoding_utils import ADDRESS, POSTAL_CODE, CITY
from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from geocoder.api.Geocoder import Geocoder
from geocoder.api.conf import VERSION, QUALITY

api_rest = Blueprint(
    "rest",
    __name__,
)


@api_rest.route("/")
def home():
    return render_template("index.html", version=VERSION)


@api_rest.route("/version")
def version():
    return jsonify(version=VERSION)


@api_rest.route("/use")
def use():
    return render_template("use_rest.html")


@api_rest.app_errorhandler(404)
def handle_404(error):
    return redirect(url_for('rest.use'))


def get_jsoned_geocoded_data(geocoder):
    json = {
        'uuid': geocoder.get_uuid(),
        'geocoded_time': datetime.strftime(geocoder.get_geocoded_date_time(), '%Y-%m-%d %H:%M:%S.%f%z'),
        'api_version': VERSION,
        'quality': QUALITY,
    }
    if geocoder.is_geocoded():
        json['data'] = geocoder.get_geocoded_data().to_dict('records')
    elif geocoder.has_errors():
        json['errors'] = geocoder.get_errors()
    else:
        json['errors'] = 'Data not geocoded !'
    return json


@api_rest.route("/geocode/<address>/<postal_code>/<city>", methods=["GET"])
def geocode_one(address, postal_code, city):
    print(address)
    print(postal_code)
    print(city)
    geocoder = Geocoder(pd.DataFrame(data={ADDRESS: address, POSTAL_CODE: postal_code, CITY: city}, index=[0]))
    geocoder.geocode()
    return jsonify(get_jsoned_geocoded_data(geocoder))


@api_rest.route("/geocode_file", methods=["POST"])
def geocode_file():
    json_as_str = request.get_json(force=True)
    try:
        data = json.loads(json_as_str)
    except (json.JSONDecodeError, TypeError):
        data = json.loads(json.dumps(json_as_str))
    data_to_geocode = pd.json_normalize(data)
    geocoder = Geocoder(data_to_geocode)
    geocoder.geocode()
    return jsonify(get_jsoned_geocoded_data(geocoder))
