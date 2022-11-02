"""
implementation of class Geocoder which will deal with requests
"""
import uuid
from datetime import datetime

import numpy as np
from Geocoding_utils import ADDRESS, POSTAL_CODE, CITY

import geocoder


class Geocoder:
    """
    class to handle geocoding of addresses through API
    """
    def __init__(self, data_to_geocode):
        """
        Initialize geocoder with data and utility attributes

        :param pandas.DataFrame data_to_geocode: must contain {"address": "...", "postal_code": "...", "city": "..."}
        """
        self.errors = []
        self.geocoded = False
        self.uuid = str(uuid.uuid1())
        self.data = data_to_geocode
        self.geocoded_date_time = None
        self.check_data_to_geocode()

    def get_geocoded_date_time(self):
        return self.geocoded_date_time

    def get_geocoded_data(self):
        """
        Returns the object's data attribute

        :return: dataframe if already geocoded otherwise None
        :rtype: pandas.DataFrame
        """
        if self.geocoded:
            return self.data
        else:  # pragma: no cover
            return None

    def check_data_to_geocode(self):
        """
        Checks input data and increment :code:`errors` attribute
        .. todo:: should be replaced by argument parser
        """
        errors = []
        for col_to_check in [ADDRESS, POSTAL_CODE, CITY]:  # pragma: no cover
            if col_to_check not in self.data.columns:
                errors = errors + [f'Column {col_to_check} is missing.']
        if len(errors) > 0:
            self.errors = errors

    def geocode(self):
        """
        Geocode data if not already geocoded and no read error(s) by calling geocoder.find
        """
        if not self.geocoded and not self.errors:
            def find(args):
                if args[0] == '98000':  # pragma: no cover
                    return np.nan, np.nan, np.nan
                else:
                    res = geocoder.find(*args)
                    return res.get('longitude', np.nan), res.get('latitude', np.nan), res.get('quality', np.nan)

            geocoded_fields = [find(args) for args in self.data[[POSTAL_CODE, CITY, ADDRESS]].fillna('').values]

            self.data['lon'], self.data['lat'], self.data['quality'] = zip(*geocoded_fields)
            self.geocoded_date_time = datetime.now()
            self.geocoded = True
